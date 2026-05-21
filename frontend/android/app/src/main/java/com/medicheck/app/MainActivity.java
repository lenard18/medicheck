package com.medicheck.app;

import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.PowerManager;
import android.provider.Settings;
import android.util.Log;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    private static final String TAG = "MediCheckMain";

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(EmergencyPlugin.class);
        super.onCreate(savedInstanceState);

        // Solicitar permisos necesarios para el servicio de emergencia
        solicitarPermisos();
    }

    private void solicitarPermisos() {
        // ── 1. Notificaciones (Android 13+) ─────────────────────────
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                    != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(
                    new String[]{ android.Manifest.permission.POST_NOTIFICATIONS },
                    1001
                );
                Log.d(TAG, "Solicitando permiso POST_NOTIFICATIONS");
            }
        }

        // ── 2. Camara y microfono para videoconsultas ────────────────
        boolean camOk  = checkSelfPermission(android.Manifest.permission.CAMERA)
                            == PackageManager.PERMISSION_GRANTED;
        boolean micOk  = checkSelfPermission(android.Manifest.permission.RECORD_AUDIO)
                            == PackageManager.PERMISSION_GRANTED;
        if (!camOk || !micOk) {
            requestPermissions(
                new String[]{
                    android.Manifest.permission.CAMERA,
                    android.Manifest.permission.RECORD_AUDIO,
                    android.Manifest.permission.MODIFY_AUDIO_SETTINGS
                },
                1002
            );
            Log.d(TAG, "Solicitando permisos CAMERA / RECORD_AUDIO");
        }

        // ── 4. Exclusion de optimizacion de bateria ──────────────────
        // Sin esto Android puede matar el servicio de emergencia
        PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
        if (pm != null && !pm.isIgnoringBatteryOptimizations(getPackageName())) {
            try {
                Intent i = new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS);
                i.setData(Uri.parse("package:" + getPackageName()));
                startActivity(i);
                Log.d(TAG, "Abriendo diálogo de optimización de batería");
            } catch (Exception e) {
                Log.w(TAG, "No se pudo abrir ajustes de batería: " + e.getMessage());
            }
        }
    }
}
