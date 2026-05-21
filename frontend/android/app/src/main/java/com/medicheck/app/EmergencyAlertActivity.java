package com.medicheck.app;

// ════════════════════════════════════════════════════════════════════
//  EmergencyAlertActivity
//
//  Se lanza cuando el servicio detecta que el usuario presiona
//  AMBOS botones de volumen al mismo tiempo.
//
//  ✅ Despierta la pantalla aunque esté apagada (WakeLock)
//  ✅ Se muestra ENCIMA de la pantalla de bloqueo
//  ✅ Pantalla parpadea en rojo
//  ✅ Barra de progreso de 7 segundos
//  ✅ Si sueltas cualquier botón → progreso vuelve atrás y cancela
//  ✅ Al completar → envía la alerta al servidor
// ════════════════════════════════════════════════════════════════════

import android.animation.ArgbEvaluator;
import android.animation.ValueAnimator;
import android.app.Activity;
import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.os.PowerManager;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.content.res.ColorStateList;
import android.util.Log;

public class EmergencyAlertActivity extends Activity {

    private static final String TAG      = "MediCheckAlert";
    private static final long   HOLD_MS  = 7_000L;  // 7 segundos
    private static final long   TICK_MS  = 50L;     // actualizar cada 50ms

    private PowerManager.WakeLock wakeLock;
    private CountDownTimer        countDownTimer;
    private ProgressBar           progressBar;
    private TextView              tvSegundos;
    private ValueAnimator         bgAnimator;
    private LinearLayout          rootLayout;

    private boolean emergenciaCompletada = false;

    // ── Seguimiento de teclas presionadas ─────────────────────────
    private boolean volUpHeld   = false;
    private boolean volDownHeld = false;
    // Última vez que cada tecla disparó onKeyDown (para detectar release)
    private long lastUpRepeatMs   = 0;
    private long lastDownRepeatMs = 0;
    private android.os.Handler holdChecker;
    private Runnable holdCheckerRunnable;

    // ══════════════════════════════════════════════════════════════
    //  CICLO DE VIDA
    // ══════════════════════════════════════════════════════════════

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Log.d(TAG, "EmergencyAlertActivity creada");

        // ── Configurar ventana para mostrarse sobre la pantalla de bloqueo ──
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
            setShowWhenLocked(true);
            setTurnScreenOn(true);
        } else {
            getWindow().addFlags(
                WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED   |
                WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON     |
                WindowManager.LayoutParams.FLAG_DISMISS_KEYGUARD
            );
        }

        // ── WakeLock: despierta la pantalla desde estado apagado ────
        PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
        if (pm != null) {
            wakeLock = pm.newWakeLock(
                PowerManager.SCREEN_BRIGHT_WAKE_LOCK |
                PowerManager.ACQUIRE_CAUSES_WAKEUP,   // ← esto enciende la pantalla
                "MediCheck:EmergencyWakeLock"
            );
            wakeLock.acquire(20_000L); // máximo 20 s
        }

        // ── Pantalla completa sin barra de título ───────────────────
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        );
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        // ── Construir UI ────────────────────────────────────────────
        construirUI();

        // ── Verificar que los botones siguen presionados (seguridad) ─
        holdChecker = new android.os.Handler();
        holdCheckerRunnable = new Runnable() {
            @Override
            public void run() {
                long ahora = System.currentTimeMillis();
                // Si ningún botón ha dado keyDown en los últimos 600ms → los soltaron
                boolean upActivo   = (ahora - lastUpRepeatMs)   < 600;
                boolean downActivo = (ahora - lastDownRepeatMs) < 600;

                if (!upActivo || !downActivo) {
                    if (!emergenciaCompletada) {
                        Log.d(TAG, "Botón suelto detectado por holdChecker — cancelando");
                        runOnUiThread(() -> cancelar());
                    }
                    return;
                }
                holdChecker.postDelayed(this, 200);
            }
        };
        // Dar 800ms de margen para que lleguen los primeros keyDown
        holdChecker.postDelayed(holdCheckerRunnable, 800);

        // ── Iniciar cuenta regresiva ────────────────────────────────
        iniciarCountdown();
    }

    // ══════════════════════════════════════════════════════════════
    //  CONSTRUCCIÓN DE LA INTERFAZ
    // ══════════════════════════════════════════════════════════════

    private void construirUI() {
        int dp = (int) getResources().getDisplayMetrics().density;

        // ── Layout raíz ─────────────────────────────────────────────
        rootLayout = new LinearLayout(this);
        rootLayout.setOrientation(LinearLayout.VERTICAL);
        rootLayout.setBackgroundColor(Color.parseColor("#CC0000"));
        rootLayout.setGravity(Gravity.CENTER);
        rootLayout.setLayoutParams(new ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        ));

        // ── Emoji 🚨 ─────────────────────────────────────────────────
        TextView tvEmoji = new TextView(this);
        tvEmoji.setText("🚨");
        tvEmoji.setTextSize(64);
        tvEmoji.setGravity(Gravity.CENTER);
        addConMargen(rootLayout, tvEmoji, 0, 0, 0, 8 * dp);

        // ── Título ───────────────────────────────────────────────────
        TextView tvTitulo = new TextView(this);
        tvTitulo.setText("ALERTA DE EMERGENCIA");
        tvTitulo.setTextSize(22);
        tvTitulo.setTextColor(Color.WHITE);
        tvTitulo.setTypeface(null, Typeface.BOLD);
        tvTitulo.setGravity(Gravity.CENTER);
        addConMargen(rootLayout, tvTitulo, 16 * dp, 0, 16 * dp, 6 * dp);

        // ── Subtítulo ────────────────────────────────────────────────
        TextView tvSub = new TextView(this);
        tvSub.setText("Mantén ambos botones de volumen\nSuelta para cancelar");
        tvSub.setTextSize(14);
        tvSub.setTextColor(Color.parseColor("#FFCCCC"));
        tvSub.setGravity(Gravity.CENTER);
        tvSub.setLineSpacing(4 * dp, 1f);
        addConMargen(rootLayout, tvSub, 16 * dp, 0, 16 * dp, 28 * dp);

        // ── Número de segundos restantes ─────────────────────────────
        tvSegundos = new TextView(this);
        tvSegundos.setText("7s");
        tvSegundos.setTextSize(64);
        tvSegundos.setTextColor(Color.WHITE);
        tvSegundos.setTypeface(null, Typeface.BOLD);
        tvSegundos.setGravity(Gravity.CENTER);
        addConMargen(rootLayout, tvSegundos, 0, 0, 0, 16 * dp);

        // ── Barra de progreso ────────────────────────────────────────
        progressBar = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progressBar.setMax(1000);
        progressBar.setProgress(0);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            progressBar.setProgressTintList(ColorStateList.valueOf(Color.WHITE));
            progressBar.setProgressBackgroundTintList(
                ColorStateList.valueOf(Color.parseColor("#55FFFFFF"))
            );
        }
        LinearLayout.LayoutParams barParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, 20 * dp
        );
        barParams.setMargins(32 * dp, 0, 32 * dp, 8 * dp);
        progressBar.setLayoutParams(barParams);
        rootLayout.addView(progressBar);

        // ── Etiquetas 0s / 7s ────────────────────────────────────────
        LinearLayout labels = new LinearLayout(this);
        labels.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams labelsParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
        );
        labelsParams.setMargins(32 * dp, 0, 32 * dp, 32 * dp);
        labels.setLayoutParams(labelsParams);

        TextView lbl0 = new TextView(this);
        lbl0.setText("0s");
        lbl0.setTextColor(Color.parseColor("#99FFFFFF"));
        lbl0.setTextSize(11);
        lbl0.setLayoutParams(new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));

        TextView lbl7 = new TextView(this);
        lbl7.setText("7s");
        lbl7.setTextColor(Color.parseColor("#99FFFFFF"));
        lbl7.setTextSize(11);
        lbl7.setGravity(Gravity.END);
        lbl7.setLayoutParams(new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));

        labels.addView(lbl0);
        labels.addView(lbl7);
        rootLayout.addView(labels);

        // ── Botón cancelar ───────────────────────────────────────────
        Button btnCancel = new Button(this);
        btnCancel.setText("✕  CANCELAR");
        btnCancel.setTextColor(Color.WHITE);
        btnCancel.setTextSize(14);
        btnCancel.setTypeface(null, Typeface.BOLD);
        btnCancel.setBackgroundColor(Color.parseColor("#55000000"));
        btnCancel.setOnClickListener(v -> cancelar());
        LinearLayout.LayoutParams btnParams = new LinearLayout.LayoutParams(
            200 * dp, 48 * dp
        );
        btnParams.gravity = Gravity.CENTER_HORIZONTAL;
        btnParams.setMargins(0, 0, 0, 0);
        btnCancel.setLayoutParams(btnParams);
        rootLayout.addView(btnCancel);

        setContentView(rootLayout);

        // ── Animación pulsante del fondo (rojo oscuro ↔ rojo vivo) ───
        bgAnimator = ValueAnimator.ofObject(
            new ArgbEvaluator(),
            Color.parseColor("#990000"),   // rojo oscuro
            Color.parseColor("#FF1111")    // rojo brillante
        );
        bgAnimator.setDuration(400);
        bgAnimator.setRepeatMode(ValueAnimator.REVERSE);
        bgAnimator.setRepeatCount(ValueAnimator.INFINITE);
        bgAnimator.addUpdateListener(anim ->
            rootLayout.setBackgroundColor((int) anim.getAnimatedValue())
        );
        bgAnimator.start();
    }

    private void addConMargen(LinearLayout parent, View v, int l, int t, int r, int b) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        );
        p.setMargins(l, t, r, b);
        v.setLayoutParams(p);
        parent.addView(v);
    }

    // ══════════════════════════════════════════════════════════════
    //  CUENTA REGRESIVA
    // ══════════════════════════════════════════════════════════════

    private void iniciarCountdown() {
        countDownTimer = new CountDownTimer(HOLD_MS, TICK_MS) {
            @Override
            public void onTick(long msRestantes) {
                long transcurrido = HOLD_MS - msRestantes;
                int  progreso     = (int) ((transcurrido * 1000L) / HOLD_MS);
                int  segs         = (int) (msRestantes / 1000) + 1;

                progressBar.setProgress(progreso);
                tvSegundos.setText(segs + "s");
            }

            @Override
            public void onFinish() {
                if (!emergenciaCompletada) {
                    progressBar.setProgress(1000);
                    tvSegundos.setText("0s");
                    completarEmergencia();
                }
            }
        }.start();
    }

    // ══════════════════════════════════════════════════════════════
    //  COMPLETAR / CANCELAR
    // ══════════════════════════════════════════════════════════════

    private void completarEmergencia() {
        emergenciaCompletada = true;
        Log.d(TAG, "✅ Emergencia completada — enviando alerta");
        // Detener parpadeo y poner fondo verde brevemente
        if (bgAnimator != null) bgAnimator.cancel();
        rootLayout.setBackgroundColor(Color.parseColor("#006633"));
        if (tvSegundos != null) tvSegundos.setText("✅");

        // Llamar al servicio para enviar la alerta HTTP
        EmergencyService.dispararAlerta(getApplicationContext());

        // Cerrar la actividad tras 2 segundos
        new android.os.Handler().postDelayed(this::finish, 2000);
    }

    private void cancelar() {
        Log.d(TAG, "✖ Emergencia cancelada por el usuario");
        if (countDownTimer != null) countDownTimer.cancel();
        if (holdChecker    != null) holdChecker.removeCallbacks(holdCheckerRunnable);
        finish();
    }

    // ══════════════════════════════════════════════════════════════
    //  DETECCIÓN DE TECLAS (el método más fiable cuando la app
    //  está visible — incluso sobre la pantalla de bloqueo)
    // ══════════════════════════════════════════════════════════════

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_VOLUME_UP) {
            volUpHeld = true;
            lastUpRepeatMs = System.currentTimeMillis();
            return true; // consumir: no cambiar volumen
        }
        if (keyCode == KeyEvent.KEYCODE_VOLUME_DOWN) {
            volDownHeld = true;
            lastDownRepeatMs = System.currentTimeMillis();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    public boolean onKeyUp(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_VOLUME_UP) {
            volUpHeld = false;
            if (!emergenciaCompletada) {
                Log.d(TAG, "Soltó VolumeUp — cancelando");
                cancelar();
            }
            return true;
        }
        if (keyCode == KeyEvent.KEYCODE_VOLUME_DOWN) {
            volDownHeld = false;
            if (!emergenciaCompletada) {
                Log.d(TAG, "Soltó VolumeDown — cancelando");
                cancelar();
            }
            return true;
        }
        return super.onKeyUp(keyCode, event);
    }

    @Override
    public void onBackPressed() {
        cancelar();
    }

    // ══════════════════════════════════════════════════════════════
    //  LIMPIEZA
    // ══════════════════════════════════════════════════════════════

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (bgAnimator    != null) bgAnimator.cancel();
        if (countDownTimer != null) countDownTimer.cancel();
        if (holdChecker    != null) holdChecker.removeCallbacks(holdCheckerRunnable);
        if (wakeLock != null && wakeLock.isHeld()) wakeLock.release();
    }
}
