package com.aiglasses.bluetooth

import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log

class BluetoothReceiver : BroadcastReceiver() {
    val pin = "0000" //此处为你要连接的蓝牙设备的初始密钥，一般为1234或0000
    val device_name = "btgps"
    lateinit var btAdapter: BluetoothAdapter

    fun setBluetoothAdapter(adapter: BluetoothAdapter) {
        btAdapter = adapter
    }

    //广播接收器，当远程蓝牙设备被发现时，回调函数onReceiver()会被执行
    @SuppressLint("MissingPermission")
    override fun onReceive(context: Context, intent: Intent) {
        val action = intent.action //得到action
        Log.i("BluetoothReceiver", "action " + action!!)
        val btDevice: BluetoothDevice?  //创建一个蓝牙device对象
        // 从Intent中获取设备对象
        btDevice = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
        if (BluetoothDevice.ACTION_FOUND == action) {  //发现设备
            Log.i(
                "BluetoothReceiver",
                "发现设备:[" + btDevice!!.name + "]" + ":" + btDevice.address
            )
            if (btDevice.name != null && btDevice.name.contains(device_name)) //设备如果有多个，第一个搜到的那个会被尝试。
            {
                if (btDevice.bondState == BluetoothDevice.BOND_NONE) {
                    Log.i("BluetoothReceiver", "attempt to bond:" + "[" + btDevice.name + "]")
                    try {
                        //通过工具类ClsUtils,调用createBond方法
                        val ret = ClsUtils.createBond(btDevice.javaClass, btDevice)
                        Log.i("BluetoothReceiver", "ClsUtils.createBond: " + ret)
                    } catch (e: Exception) {
                        // TODO Auto-generated catch block
                        Log.e("BluetoothReceiver", "发现设备error" + e)

                    }
                } else if (btDevice.bondState == BluetoothDevice.BOND_BONDED) {
                    btAdapter.cancelDiscovery()
                    Log.i("BluetoothReceiver", "设备已配对，停止扫描")
                }

            } else {
                Log.i("BluetoothReceiver", "没有找到目标设备")
            }
        } else if (action == BluetoothDevice.ACTION_PAIRING_REQUEST) //再次得到的action，会等于PAIRING_REQUEST
        {
            if (btDevice!!.name != null && btDevice.name.contains(device_name)) {
                Log.i("BluetoothReceiver", "OKOKOK")
                try {

                    //1.确认配对
//                    btDevice.setPairingConfirmation(true)
//                    ClsUtils.setPairingConfirmation(btDevice.javaClass, btDevice, true)
                    //2.终止有序广播
                    Log.d(
                        "BluetoothReceiver",
                        "isOrderedBroadcast:$isOrderedBroadcast,isInitialStickyBroadcast:$isInitialStickyBroadcast"
                    )
                    abortBroadcast() //如果没有将广播终止，则会出现一个一闪而过的配对框。
                    //3.调用setPin方法进行配对...
                    val ret = btDevice.setPin(pin.toByteArray())
//                    val ret = ClsUtils.setPin(btDevice.javaClass, btDevice, pin)
                    Log.i("BluetoothReceiver", "ClsUtils.setPin: " + ret)

                } catch (e: Exception) {
                    // TODO Auto-generated catch block
                    Log.e("BluetoothReceiver", "配对设备error" + e)
                }
            } else {
                Log.i("BluetoothReceiver", "这个设备不是目标蓝牙设备")
            }
        }
    }
}
