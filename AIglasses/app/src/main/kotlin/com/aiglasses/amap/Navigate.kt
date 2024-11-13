package com.aiglasses.amap

import android.content.Context
import android.text.Editable
import android.text.TextWatcher
import android.util.Log
import android.view.View
import android.widget.EditText
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.aiglasses.MainActivity
import com.aiglasses.ShowMessageUtil
import com.amap.api.maps.AMap
import com.amap.api.maps.CameraUpdateFactory
import com.amap.api.maps.MapView
import com.amap.api.navi.AMapNavi
import com.amap.api.navi.AMapNaviListener
import com.amap.api.navi.NaviSetting
import com.amap.api.navi.enums.NaviType
import com.amap.api.navi.model.AMapCalcRouteResult
import com.amap.api.navi.model.AMapLaneInfo
import com.amap.api.navi.model.AMapModelCross
import com.amap.api.navi.model.AMapNaviCameraInfo
import com.amap.api.navi.model.AMapNaviCross
import com.amap.api.navi.model.AMapNaviLocation
import com.amap.api.navi.model.AMapNaviPath
import com.amap.api.navi.model.AMapNaviRouteNotifyData
import com.amap.api.navi.model.AMapNaviTrafficFacilityInfo
import com.amap.api.navi.model.AMapServiceAreaInfo
import com.amap.api.navi.model.AimLessModeCongestionInfo
import com.amap.api.navi.model.AimLessModeStat
import com.amap.api.navi.model.NaviInfo
import com.amap.api.navi.model.NaviLatLng
import com.amap.api.navi.view.RouteOverLay
import com.amap.api.services.help.Inputtips
import com.amap.api.services.help.Inputtips.InputtipsListener
import com.amap.api.services.help.InputtipsQuery
import com.amap.api.services.help.Tip


class Navigate : InputtipsListener, TextWatcher,
    RvAdapter.OnItemClickListener, AMapNaviListener {

    companion object {

        private var naviPaths = HashMap<Int, AMapNaviPath>()

        //dstPoint输入终点经纬度，自动尝试导航
        fun tryNavi(dstPoint: NaviLatLng) {
            try {
                AMapNavi.getInstance(ShowMessageUtil.getAppContext())
                    .calculateWalkRoute(dstPoint)
                Log.i("calculateWalkRoute", dstPoint.toString())
            } catch (e: Exception) {
                Log.e("calculateWalkRoute", e.message!!)
            }
        }

    }

    private var rvAdapter: RvAdapter? = null
    private var inputtips: Inputtips? = null
    private var aMapNavi: AMapNavi? = null
    private var searchEditText: EditText? = null
    private var searchRecyclerView: RecyclerView? = null

    private lateinit var applicationContext: Context
    private var aMap: AMap? = null
    private val containerRouteOverLay = ArrayList<RouteOverLay>()
    private val list = ArrayList<Tip>()

    fun initNavi(mainAtv: MainActivity, mapView: MapView) {
        applicationContext = ShowMessageUtil.getAppContext()
        aMapNavi = AMapNavi.getInstance(applicationContext)

        aMap = mapView.map
        searchEditText = mainAtv.editText
        searchRecyclerView = mainAtv.recyclerView
        searchEditText!!.bringToFront()
        searchRecyclerView!!.bringToFront()

        searchEditText!!.addTextChangedListener(this)
        searchRecyclerView!!.layoutManager =
            LinearLayoutManager(mainAtv, RecyclerView.VERTICAL, false)
        rvAdapter = RvAdapter(list, mainAtv, searchRecyclerView!!)
        rvAdapter!!.setmOnItemClickListener(this)
        searchRecyclerView!!.adapter = rvAdapter
        inputtips = Inputtips(mainAtv, null as InputtipsQuery?)
        inputtips!!.setInputtipsListener(this)

        //这是隐私合规接口，如果不加，可能出现地图加载不出来的问题
        NaviSetting.updatePrivacyShow(applicationContext, true, true)
        NaviSetting.updatePrivacyAgree(applicationContext, true)

        if (aMapNavi != null) {
            //设置内置语音播报
            aMapNavi!!.setUseInnerVoice(true, false)
            aMapNavi!!.addAMapNaviListener(this)
        }
        restoreMap(naviPaths)
    }


    fun cancelNavi() {
        AMapNavi.getInstance(applicationContext).stopNavi()
        naviPaths.clear()
        erasePaths()
        ShowMessageUtil.showMessage("停止导航")
    }

    private fun drawPaths(aMap: AMap, currentPaths: HashMap<Int, AMapNaviPath>) {
        for (path in currentPaths) {
            val rol = RouteOverLay(aMap, path.component2(), applicationContext)
            rol.addToMap()
            containerRouteOverLay.add(rol)
        }
    }

    private fun erasePaths() {
        for (rol in containerRouteOverLay) {
            rol.removeFromMap()
        }
        containerRouteOverLay.clear()
    }

    private fun restoreMap(currentPaths: HashMap<Int, AMapNaviPath>) {
        erasePaths()
        if (aMap != null) {
            drawPaths(aMap!!, currentPaths)
            aMap!!.moveCamera(CameraUpdateFactory.zoomTo(19f))
        }//设置地图的放缩
    }

    override fun beforeTextChanged(charSequence: CharSequence, i: Int, i1: Int, i2: Int) {}
    override fun onTextChanged(charSequence: CharSequence, i: Int, i1: Int, i2: Int) {
        val inputtipsQuery = InputtipsQuery(charSequence.toString(), null)
        inputtipsQuery.cityLimit = true
        inputtips!!.query = inputtipsQuery
        inputtips!!.requestInputtipsAsyn()
    }

    override fun afterTextChanged(editable: Editable) {}
    override fun onItemClick(recyclerView: RecyclerView?, view: View?, position: Int, data: Tip?) {
        Log.i("TAG", "onItemClick:  点击了" + position + "条")
        //得到点击的坐标
        val point = data!!.point
        Log.i("Tag", "坐标为$point")
        //得到经纬度
        searchEditText?.text?.clear()
        rvAdapter!!.clearData()

        tryNavi(NaviLatLng(point.latitude, point.longitude))
    }

    override fun onGetInputtips(list: List<Tip>, i: Int) {
        rvAdapter!!.setData(list)
    }

    override fun onInitNaviFailure() {
        ShowMessageUtil.showMessage("启动导航失败")
    }

    override fun onInitNaviSuccess() {
        //   TODO("Not yet implemented")
    }

    override fun onStartNavi(p0: Int) {
        //   TODO("Not yet implemented")
    }

    override fun onTrafficStatusUpdate() {
        //   TODO("Not yet implemented")
    }

    override fun onLocationChange(p0: AMapNaviLocation?) {
        //   TODO("Not yet implemented")
    }

    override fun onGetNavigationText(p0: Int, p1: String?) {
        //   TODO("Not yet implemented")
    }

    @Deprecated("Deprecated in Java")
    override fun onGetNavigationText(p0: String?) {
        //   TODO("Not yet implemented")
    }

    override fun onEndEmulatorNavi() {
        //   TODO("Not yet implemented")
    }

    override fun onArriveDestination() {
        //   TODO("Not yet implemented")
    }

    @Deprecated("Deprecated in Java")
    override fun onCalculateRouteFailure(p0: Int) {
        //   TODO("Not yet implemented")
    }

    override fun onCalculateRouteFailure(p0: AMapCalcRouteResult?) {
        Log.e("calculateWalkRoute", "路线规划失败")
        ShowMessageUtil.showMessage("路线规划失败")
    }

    override fun onReCalculateRouteForYaw() {
        //   TODO("Not yet implemented")
    }

    override fun onReCalculateRouteForTrafficJam() {
        //   TODO("Not yet implemented")
    }

    override fun onArrivedWayPoint(p0: Int) {
        //   TODO("Not yet implemented")
    }

    override fun onGpsOpenStatus(p0: Boolean) {
        //   TODO("Not yet implemented")
    }

    override fun onNaviInfoUpdate(p0: NaviInfo?) {
        //   TODO("Not yet implemented")
    }

    override fun updateCameraInfo(p0: Array<out AMapNaviCameraInfo>?) {
        //   TODO("Not yet implemented")
    }

    override fun updateIntervalCameraInfo(
        p0: AMapNaviCameraInfo?,
        p1: AMapNaviCameraInfo?,
        p2: Int
    ) {
        //   TODO("Not yet implemented")
    }

    override fun onServiceAreaUpdate(p0: Array<out AMapServiceAreaInfo>?) {
        //   TODO("Not yet implemented")
    }

    override fun showCross(p0: AMapNaviCross?) {
        //   TODO("Not yet implemented")
    }

    override fun hideCross() {
        //   TODO("Not yet implemented")
    }

    override fun showModeCross(p0: AMapModelCross?) {
        //   TODO("Not yet implemented")
    }

    override fun hideModeCross() {
        //   TODO("Not yet implemented")
    }

    @Deprecated("Deprecated in Java")
    override fun showLaneInfo(p0: Array<out AMapLaneInfo>?, p1: ByteArray?, p2: ByteArray?) {
        //   TODO("Not yet implemented")
    }

    override fun showLaneInfo(p0: AMapLaneInfo?) {
        //   TODO("Not yet implemented")
    }

    override fun hideLaneInfo() {
        //   TODO("Not yet implemented")
    }

    @Deprecated("Deprecated in Java")
    override fun onCalculateRouteSuccess(p0: IntArray?) {
        //   TODO("Not yet implemented")
    }

    override fun onCalculateRouteSuccess(routeResult: AMapCalcRouteResult?) {
        naviPaths = AMapNavi.getInstance(applicationContext).naviPaths
        restoreMap(naviPaths)
        AMapNavi.getInstance(applicationContext).startNavi(NaviType.GPS)
    }

    @Deprecated("Deprecated in Java")
    override fun notifyParallelRoad(p0: Int) {
        //   TODO("Not yet implemented")
    }

    @Deprecated("Deprecated in Java")
    override fun OnUpdateTrafficFacility(p0: Array<out AMapNaviTrafficFacilityInfo>?) {
        //   TODO("Not yet implemented")
    }

    @Deprecated("Deprecated in Java")
    override fun OnUpdateTrafficFacility(p0: AMapNaviTrafficFacilityInfo?) {
        //   TODO("Not yet implemented")
    }

    @Deprecated("Deprecated in Java")
    override fun updateAimlessModeStatistics(p0: AimLessModeStat?) {
        //   TODO("Not yet implemented")
    }

    @Deprecated("Deprecated in Java")
    override fun updateAimlessModeCongestionInfo(p0: AimLessModeCongestionInfo?) {
        //   TODO("Not yet implemented")
    }

    override fun onPlayRing(p0: Int) {
        //   TODO("Not yet implemented")
    }

    override fun onNaviRouteNotify(p0: AMapNaviRouteNotifyData?) {
        //   TODO("Not yet implemented")
    }

    override fun onGpsSignalWeak(p0: Boolean) {
        //   TODO("Not yet implemented")
    }
}
