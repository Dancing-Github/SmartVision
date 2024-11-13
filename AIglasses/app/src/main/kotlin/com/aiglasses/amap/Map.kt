package com.aiglasses.amap

import android.os.Bundle
import android.util.Log
import com.aiglasses.ShowMessageUtil
import com.aiglasses.network.HttpUtil.update_device_location
import com.amap.api.maps.AMap
import com.amap.api.maps.AMap.OnMyLocationChangeListener
import com.amap.api.maps.CameraUpdateFactory
import com.amap.api.maps.MapView
import com.amap.api.maps.MapsInitializer
import com.amap.api.maps.model.MyLocationStyle
import com.amap.api.navi.model.NaviLatLng

class Map {

    companion object {
        private const val TAG = "MapShow"
        private val myLocationChangeListener = OnMyLocationChangeListener { location ->

            // 定位回调监听
            if (location != null) {
                Log.i(
                    TAG,
                    "onMyLocationChange 定位经纬度， lat: " + location.latitude + " lng: " + location.longitude
                )
                val bundle: Bundle? = location.extras
                if (bundle != null) {
                    val errorCode: Int = bundle.getInt(MyLocationStyle.ERROR_CODE)
                    val errorInfo: String? = bundle.getString(MyLocationStyle.ERROR_INFO)
                    // 定位类型，可能为GPS WIFI等，具体可以参考官网的定位SDK介绍
                    val locationType: Int = bundle.getInt(MyLocationStyle.LOCATION_TYPE)
                    val msg = "code: $errorCode errorInfo: $errorInfo locationType: $locationType"
                    if (errorCode == 0) {
                        update_device_location(NaviLatLng(location.latitude, location.longitude))
                        Log.d(TAG, "定位信息，" + msg)
                    } else {
                        Log.e(TAG, "定位错误，" + msg)
                    }

                } else {
                    Log.e(TAG, "定位错误， bundle is null")
                }
            } else {
                Log.e(TAG, "定位失败， location is null")
            }

        }
    }

    private val myLocationStyle = MyLocationStyle()
    private var aMap: AMap? = null
    private var mapView: MapView? = null

    fun initMap(savedInstanceState: Bundle?, mapV: MapView) {
        mapV.onCreate(savedInstanceState)

        val applicationContext = ShowMessageUtil.getAppContext()
        MapsInitializer.updatePrivacyShow(applicationContext, true, true)
        MapsInitializer.updatePrivacyAgree(applicationContext, true)

        //初始化地图控件
        mapView = mapV
        aMap = mapView!!.map

        //持续定位
        myLocationStyle.myLocationType(MyLocationStyle.LOCATION_TYPE_LOCATION_ROTATE)
        //设置连续定位模式下定位间隔
        myLocationStyle.interval(2000)

        aMap!!.myLocationStyle = myLocationStyle //设置定位蓝点的Style
        aMap!!.isMyLocationEnabled = true // 设置为true表示启动显示定位蓝点，false表示隐藏定位蓝点并不进行定位，默认是false。
        aMap!!.moveCamera(CameraUpdateFactory.zoomTo(18f))
        aMap!!.setOnMyLocationChangeListener(myLocationChangeListener)
    }



}
