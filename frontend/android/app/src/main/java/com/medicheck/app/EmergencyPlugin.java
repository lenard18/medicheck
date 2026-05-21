package com.medicheck.app;

// ════════════════════════════════════════════════════════════════════
//  EmergencyPlugin — Puente entre Vue/JavaScript y el servicio nativo
//
//  Expone dos métodos al JavaScript de la app:
//  - iniciarServicio(token, serverUrl) → arranca el servicio en background
//  - detenerServicio()                 → detiene el servicio
// ════════════════════════════════════════════════════════════════════

import android.content.Intent;
import android.os.Build;
import android.util.Log;

import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "Emergency")
public class EmergencyPlugin extends Plugin {

    private static final String TAG = "EmergencyPlugin";

    /**
     * Llamado desde Vue cuando el usuario inicia sesión.
     * Arranca el servicio en segundo plano con el token JWT.
     *
     * Uso en Vue:
     *   import { registerPlugin } from '@capacitor/core'
     *   const Emergency = registerPlugin('Emergency')
     *   Emergency.iniciarServicio({ token: '...', serverUrl: 'http://...' })
     */
    @PluginMethod
    public void iniciarServicio(PluginCall call) {
        String token     = call.getString("token", "");
        String serverUrl = call.getString("serverUrl", "");

        Log.d(TAG, "Iniciando servicio de emergencia. URL=" + serverUrl);

        Intent intent = new Intent(getContext(), EmergencyService.class);
        intent.putExtra("token",     token);
        intent.putExtra("serverUrl", serverUrl);

        // Foreground service (requerido en Android 8+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            getContext().startForegroundService(intent);
        } else {
            getContext().startService(intent);
        }

        call.resolve();
    }

    /**
     * Llamado cuando el usuario cierra sesión.
     * Detiene el servicio en segundo plano.
     */
    @PluginMethod
    public void detenerServicio(PluginCall call) {
        Log.d(TAG, "Deteniendo servicio de emergencia");
        Intent intent = new Intent(getContext(), EmergencyService.class);
        getContext().stopService(intent);
        call.resolve();
    }
}
