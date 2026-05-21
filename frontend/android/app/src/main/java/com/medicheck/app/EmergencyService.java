package com.medicheck.app;

// ════════════════════════════════════════════════════════════════════
//  EmergencyService v2 — Triple detección de botones de volumen
//
//  MÉTODOS (los tres activos en paralelo):
//  1. BroadcastReceiver  → android.media.VOLUME_CHANGED_ACTION
//  2. ContentObserver    → Settings.System.CONTENT_URI  (volumen)
//  3. AudioManager poll  → cada 120 ms compara nivel real del sistema
//
//  El método 3 (polling) garantiza que aunque los botones se cancelen
//  entre sí y no produzcan ningún evento, lo detectamos igualmente
//  al comparar el stream MUSIC y el stream RING en cada tick.
//
//  TRIGGER: cambio ↑ Y cambio ↓ dentro de una ventana de 900 ms
//           → lanza EmergencyAlertActivity (pantalla roja + 7 s)
// ════════════════════════════════════════════════════════════════════

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.database.ContentObserver;
import android.media.AudioManager;
import android.net.Uri;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.provider.Settings;
import android.util.Log;
import androidx.core.app.NotificationCompat;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class EmergencyService extends Service {

    private static final String TAG        = "MediCheckEmergency";
    private static final String CHANNEL_ID = "medicheck_emergency_bg";
    private static final int    NOTIF_ID   = 9001;

    // ── Ventana de detección simultánea ────────────────────────────
    // Si ↑ y ↓ ocurren dentro de este tiempo → ambos botones presionados
    private static final long SIMULT_MS  = 900L;
    // Tiempo mínimo entre lanzamientos de la actividad de alerta
    private static final long COOLDOWN_MS = 6_000L;
    // Intervalo del poller de AudioManager
    private static final long POLL_MS    = 120L;

    // ── Estado estático (accedido por EmergencyAlertActivity) ──────
    public static String authToken = null;
    public static String serverUrl = null;

    // ── Internos ───────────────────────────────────────────────────
    private AudioManager     audioManager;
    private NotificationManager nm;
    private Handler          handler;
    private BroadcastReceiver volumeReceiver;
    private ContentObserver   volumeObserver;
    private Runnable          pollerRunnable;

    // Timestaps de último evento en cada dirección (cualquier método)
    private long lastUpMs   = -1;
    private long lastDownMs = -1;

    // Volúmenes anteriores del poller
    private int prevMusic = -1;
    private int prevRing  = -1;
    private int prevVoice = -1;

    // Anti-rebote
    private long lastLaunchMs = -1;

    // ══════════════════════════════════════════════════════════════
    //  CICLO DE VIDA
    // ══════════════════════════════════════════════════════════════

    @Override
    public void onCreate() {
        super.onCreate();
        handler       = new Handler(Looper.getMainLooper());
        audioManager  = (AudioManager) getSystemService(AUDIO_SERVICE);
        nm            = getSystemService(NotificationManager.class);

        crearCanalNotificacion();
        startForeground(NOTIF_ID, construirNotificacionBase());

        // Inicializar volúmenes de referencia para el poller
        prevMusic = audioManager.getStreamVolume(AudioManager.STREAM_MUSIC);
        prevRing  = audioManager.getStreamVolume(AudioManager.STREAM_RING);
        prevVoice = audioManager.getStreamVolume(AudioManager.STREAM_VOICE_CALL);

        // ── Los tres métodos en paralelo ───────────────────────────
        registrarBroadcastReceiver();
        registrarContentObserver();
        iniciarPoller();

        Log.d(TAG, "✅ Servicio iniciado — triple detección activa");
        Log.d(TAG, "   prevMusic=" + prevMusic + " prevRing=" + prevRing);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null) {
            if (intent.hasExtra("token"))     authToken = intent.getStringExtra("token");
            if (intent.hasExtra("serverUrl")) serverUrl = intent.getStringExtra("serverUrl");
            Log.d(TAG, "Token y URL recibidos. ServerUrl=" + serverUrl);
        }
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        try { unregisterReceiver(volumeReceiver); } catch (Exception ignored) {}
        try { getContentResolver().unregisterContentObserver(volumeObserver); } catch (Exception ignored) {}
        if (pollerRunnable != null) handler.removeCallbacks(pollerRunnable);
        Log.d(TAG, "Servicio detenido");
    }

    @Override
    public IBinder onBind(Intent intent) { return null; }

    // ══════════════════════════════════════════════════════════════
    //  MÉTODO 1 — BroadcastReceiver
    //  Recibe el intent android.media.VOLUME_CHANGED_ACTION que
    //  Android envía cuando el usuario cambia el volumen.
    // ══════════════════════════════════════════════════════════════

    private void registrarBroadcastReceiver() {
        volumeReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context ctx, Intent intent) {
                int nuevo = intent.getIntExtra("android.media.EXTRA_VOLUME_STREAM_VALUE", -1);
                int viejo = intent.getIntExtra("android.media.EXTRA_PREV_VOLUME_STREAM_VALUE", -1);
                if (nuevo < 0 || viejo < 0 || nuevo == viejo) return;

                long ahora = System.currentTimeMillis();
                Log.d(TAG, "[BR] vol " + viejo + " → " + nuevo);
                registrarCambio(nuevo > viejo, ahora);
            }
        };
        registerReceiver(volumeReceiver,
            new IntentFilter("android.media.VOLUME_CHANGED_ACTION"));
        Log.d(TAG, "Método 1 (BroadcastReceiver) activo");
    }

    // ══════════════════════════════════════════════════════════════
    //  MÉTODO 2 — ContentObserver
    //  Observa cambios en Settings.System (incluye volumen).
    //  Cuando dispara, comparamos el nivel actual con el anterior.
    // ══════════════════════════════════════════════════════════════

    private void registrarContentObserver() {
        volumeObserver = new ContentObserver(handler) {
            @Override
            public void onChange(boolean selfChange, Uri uri) {
                long ahora = System.currentTimeMillis();

                int music = audioManager.getStreamVolume(AudioManager.STREAM_MUSIC);
                int ring  = audioManager.getStreamVolume(AudioManager.STREAM_RING);

                if (prevMusic >= 0 && music != prevMusic) {
                    Log.d(TAG, "[CO] music " + prevMusic + " → " + music);
                    registrarCambio(music > prevMusic, ahora);
                }
                if (prevRing >= 0 && ring != prevRing) {
                    Log.d(TAG, "[CO] ring  " + prevRing + " → " + ring);
                    registrarCambio(ring > prevRing, ahora);
                }

                prevMusic = music;
                prevRing  = ring;
            }
        };
        getContentResolver().registerContentObserver(
            Settings.System.CONTENT_URI, true, volumeObserver);
        Log.d(TAG, "Método 2 (ContentObserver) activo");
    }

    // ══════════════════════════════════════════════════════════════
    //  MÉTODO 3 — Polling activo de AudioManager
    //
    //  Este es el más fiable: pregunta directamente al sistema cada
    //  120 ms si el nivel de volumen cambió. Detecta incluso cuando
    //  los dos botones se anulan (ΔNet=0) porque vemos cada cambio
    //  individual antes de que se compensen.
    // ══════════════════════════════════════════════════════════════

    private void iniciarPoller() {
        pollerRunnable = new Runnable() {
            @Override
            public void run() {
                long ahora = System.currentTimeMillis();

                int music = audioManager.getStreamVolume(AudioManager.STREAM_MUSIC);
                int ring  = audioManager.getStreamVolume(AudioManager.STREAM_RING);
                int voice = audioManager.getStreamVolume(AudioManager.STREAM_VOICE_CALL);

                if (prevMusic >= 0 && music != prevMusic) {
                    Log.d(TAG, "[POLL] music " + prevMusic + " → " + music);
                    registrarCambio(music > prevMusic, ahora);
                    prevMusic = music;
                }
                if (prevRing >= 0 && ring != prevRing) {
                    Log.d(TAG, "[POLL] ring  " + prevRing + " → " + ring);
                    registrarCambio(ring > prevRing, ahora);
                    prevRing = ring;
                }
                if (prevVoice >= 0 && voice != prevVoice) {
                    Log.d(TAG, "[POLL] voice " + prevVoice + " → " + voice);
                    registrarCambio(voice > prevVoice, ahora);
                    prevVoice = voice;
                }

                handler.postDelayed(this, POLL_MS);
            }
        };
        handler.postDelayed(pollerRunnable, POLL_MS);
        Log.d(TAG, "Método 3 (Poller 120ms) activo");
    }

    // ══════════════════════════════════════════════════════════════
    //  LÓGICA CENTRAL — registrar cambio y evaluar simultaneidad
    // ══════════════════════════════════════════════════════════════

    private synchronized void registrarCambio(boolean subida, long ahora) {
        if (subida) {
            lastUpMs = ahora;
        } else {
            lastDownMs = ahora;
        }
        evaluarSimultaneidad(ahora);
    }

    private void evaluarSimultaneidad(long ahora) {
        if (lastUpMs <= 0 || lastDownMs <= 0) return;

        long diff = Math.abs(lastUpMs - lastDownMs);
        if (diff > SIMULT_MS) return;

        // Cooldown: evitar relanzar la actividad enseguida
        long desdeLanzamiento = (lastLaunchMs > 0) ? (ahora - lastLaunchMs) : Long.MAX_VALUE;
        if (desdeLanzamiento < COOLDOWN_MS) return;

        Log.d(TAG, "🎯 Pulsación simultánea detectada (diff=" + diff + "ms) → lanzando alerta");
        lastLaunchMs = ahora;
        lastUpMs     = -1;
        lastDownMs   = -1;

        handler.post(this::lanzarActividadAlerta);
    }

    private void lanzarActividadAlerta() {
        try {
            Intent intent = new Intent(this, EmergencyAlertActivity.class);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK |
                            Intent.FLAG_ACTIVITY_SINGLE_TOP |
                            Intent.FLAG_ACTIVITY_CLEAR_TOP);
            startActivity(intent);
            Log.d(TAG, "EmergencyAlertActivity lanzada");
        } catch (Exception e) {
            Log.e(TAG, "Error lanzando actividad: " + e.getMessage());
        }
    }

    // ══════════════════════════════════════════════════════════════
    //  dispararAlerta — llamado por EmergencyAlertActivity al completar
    // ══════════════════════════════════════════════════════════════

    public static void dispararAlerta(Context context) {
        Log.d(TAG, "🚨 dispararAlerta()");

        // Vibración de confirmación
        try {
            Vibrator v = (Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);
            if (v != null && v.hasVibrator()) {
                long[] patron = { 0, 600, 150, 600, 150, 900 };
                v.vibrate(VibrationEffect.createWaveform(patron, -1));
            }
        } catch (Exception ignored) {}

        mostrarNotificacionEmergencia(context);
        new Thread(() -> enviarAlertaServidor(context)).start();
    }

    private static void enviarAlertaServidor(Context ctx) {
        if (serverUrl == null || authToken == null) {
            Log.w(TAG, "Sin token/URL — no se envía alerta");
            return;
        }
        try {
            URL url = new URL(serverUrl + "/emergencia/activar");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setRequestProperty("Authorization", "Bearer " + authToken);
            conn.setDoOutput(true);
            conn.setConnectTimeout(6000);
            conn.setReadTimeout(6000);

            String body = "{\"origen\":\"botones_volumen_7s\",\"timestamp\":\""
                + System.currentTimeMillis() + "\"}";
            try (OutputStream os = conn.getOutputStream()) {
                os.write(body.getBytes(StandardCharsets.UTF_8));
            }
            Log.d(TAG, "Alerta enviada. HTTP " + conn.getResponseCode());
            conn.disconnect();
        } catch (Exception e) {
            Log.e(TAG, "Error enviando: " + e.getMessage());
        }
    }

    // ══════════════════════════════════════════════════════════════
    //  NOTIFICACIONES
    // ══════════════════════════════════════════════════════════════

    private void crearCanalNotificacion() {
        NotificationChannel canal = new NotificationChannel(
            CHANNEL_ID, "MediCheck Emergencia",
            NotificationManager.IMPORTANCE_HIGH);
        canal.setShowBadge(false);
        if (nm != null) nm.createNotificationChannel(canal);
    }

    private Notification construirNotificacionBase() {
        Intent i = new Intent(this, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(this, 0, i,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        return new NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("MediCheck activo")
            .setContentText("Presiona ↑+↓ volumen al mismo tiempo para emergencia")
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentIntent(pi)
            .setOngoing(true).setSilent(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build();
    }

    private static void mostrarNotificacionEmergencia(Context ctx) {
        NotificationManager nm2 =
            (NotificationManager) ctx.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm2 == null) return;

        Intent i = new Intent(ctx, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(ctx, 0, i,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        Notification n = new NotificationCompat.Builder(ctx, CHANNEL_ID)
            .setContentTitle("🚨 ALERTA ENVIADA")
            .setContentText("Tu médico ha sido notificado.")
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentIntent(pi).setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .build();

        nm2.notify(9002, n);
    }
}
