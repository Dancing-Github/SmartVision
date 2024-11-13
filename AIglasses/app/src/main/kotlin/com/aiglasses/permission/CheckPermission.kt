package com.aiglasses.permission

import android.Manifest
import android.app.Activity
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Environment
import android.provider.Settings
import android.util.Log
import androidx.appcompat.app.AlertDialog
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.aiglasses.MainActivity
import com.aiglasses.ShowMessageUtil

object CheckPermission {
    private var dialog: AlertDialog? = null
    private var haveStoragePermission = false

    private const val ACCESS_NETWORK_STATE_PERMISSION = 10001
    private const val RECORD_AUDIO_PERMISSION = 10002
    private const val CAMERA_PERMISSION = 10003 //标识申请的是NETWORK权限
    private const val EXTERNAL_STORAGE_PERMISSION = 10004

    private const val BLUETOOTH_PERMISSION = 10005
    private const val BLUETOOTH_ADMIN_PERMISSION = 10006
    private const val BLUETOOTH_CONNECT_PERMISSION = 10007
    private const val BLUETOOTH_SCAN_PERMISSION = 10008
    private const val BLUETOOTH_ADVERTISE_PERMISSION = 10009

    private const val FINE_LOCATION_PERMISSION = 100010
    private const val COARSE_LOCATION_PERMISSION = 10011


    private val PERMISSIONS_STORAGE = arrayOf(
        Manifest.permission.READ_EXTERNAL_STORAGE,
        Manifest.permission.WRITE_EXTERNAL_STORAGE,
    )

    fun onRequestPermissionsResult(
        requestCode: Int,
        mainAtv: MainActivity,
        grantResults: IntArray
    ) {
        var msg = ""
        when (requestCode) {
            EXTERNAL_STORAGE_PERMISSION -> msg = "储存"
            RECORD_AUDIO_PERMISSION -> msg = "录音"

            BLUETOOTH_PERMISSION -> msg = "蓝牙"
            BLUETOOTH_ADMIN_PERMISSION -> msg = "蓝牙Admin"
            BLUETOOTH_CONNECT_PERMISSION -> msg = "蓝牙Connect"
            BLUETOOTH_SCAN_PERMISSION -> msg = "蓝牙Scan"
            BLUETOOTH_ADVERTISE_PERMISSION -> msg = "蓝牙Advertise"

            FINE_LOCATION_PERMISSION -> msg = "准确定位"
            COARSE_LOCATION_PERMISSION -> msg = "粗略定位"
        }
        if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            if (requestCode == EXTERNAL_STORAGE_PERMISSION) {
                haveStoragePermission = true
            }
//            ShowMessageUtil.showMessage(msg + "授权成功！")
        } else {
            if (requestCode == EXTERNAL_STORAGE_PERMISSION) {
                haveStoragePermission = false
            }
            ShowMessageUtil.showMessage(msg + "授权拒绝！")
        }
    }

    private fun isAndroid12() = Build.VERSION.SDK_INT >= Build.VERSION_CODES.S


    fun checkPermission(context: Context) {
        fun check(permis: String, code: Int) {
            //检查权限（NEED_PERMISSION）是否被授权 PackageManager.PERMISSION_GRANTED表示同意授权
            if (ContextCompat.checkSelfPermission(
                    context, permis
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                ActivityCompat.requestPermissions(
                    context as Activity, arrayOf(permis), code
                )
            }
        }
        check(Manifest.permission.CAMERA, CAMERA_PERMISSION)
        check(Manifest.permission.RECORD_AUDIO, RECORD_AUDIO_PERMISSION)
        check(Manifest.permission.ACCESS_NETWORK_STATE, ACCESS_NETWORK_STATE_PERMISSION)
        //是Android12
        if (isAndroid12()) {
            //检查是否有BLUETOOTH_CONNECT权限
            check(Manifest.permission.BLUETOOTH_CONNECT, BLUETOOTH_CONNECT_PERMISSION)
            check(Manifest.permission.BLUETOOTH_SCAN, BLUETOOTH_SCAN_PERMISSION)
            check(Manifest.permission.BLUETOOTH_ADVERTISE, BLUETOOTH_ADVERTISE_PERMISSION)
        } else {
            check(Manifest.permission.BLUETOOTH, BLUETOOTH_PERMISSION)
            check(Manifest.permission.BLUETOOTH_ADMIN, BLUETOOTH_ADMIN_PERMISSION)
        }

        check(Manifest.permission.ACCESS_FINE_LOCATION, FINE_LOCATION_PERMISSION)
        check(Manifest.permission.ACCESS_COARSE_LOCATION, COARSE_LOCATION_PERMISSION)


        if (Build.VERSION.SDK_INT >= 30) {
            if (!Environment.isExternalStorageManager()) {
                if (dialog != null) {
                    dialog!!.dismiss()
                    dialog = null
                }
                dialog = AlertDialog.Builder(context).setTitle("提示") //设置标题
                    .setMessage("请开启文件访问权限，否则无法正常使用本应用！").setNegativeButton(
                        "取消"
                    ) { dialog, _ -> dialog.dismiss() }.setPositiveButton(
                        "确定"
                    ) { dialog, _ ->
                        dialog.dismiss()
                        val intent = Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                        context.startActivity(intent)
                    }.create()
                dialog!!.show()
            } else {
                haveStoragePermission = true
                Log.i("swyLog", "Android 11以上，当前已有权限")
            }
        } else {

            if (ActivityCompat.checkSelfPermission(
                    context, Manifest.permission.READ_EXTERNAL_STORAGE
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                //申请权限
                if (dialog != null) {
                    dialog!!.dismiss()
                    dialog = null
                }
                dialog = AlertDialog.Builder(context).setTitle("提示") //设置标题
                    .setMessage("请开启文件访问权限，否则无法正常使用本应用！").setPositiveButton(
                        "确定"
                    ) { dialog, _ ->
                        dialog.dismiss()
                        ActivityCompat.requestPermissions(
                            context as Activity,
                            PERMISSIONS_STORAGE,
                            EXTERNAL_STORAGE_PERMISSION
                        )
                    }.create()
                dialog!!.show()
            } else {
                haveStoragePermission = true
                Log.i("swyLog", "Android 6.0以上，11以下，当前已有权限")
            }

        }
    }
}