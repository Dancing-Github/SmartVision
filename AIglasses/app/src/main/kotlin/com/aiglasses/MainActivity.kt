package com.aiglasses

import android.annotation.SuppressLint
import android.app.Activity
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.content.Intent
import android.content.IntentFilter
import android.os.Bundle
import android.os.PersistableBundle
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.view.PreviewView
import androidx.recyclerview.widget.RecyclerView
import com.aiglasses.amap.Map
import com.aiglasses.amap.Navigate
import com.aiglasses.audio.Recorder
import com.aiglasses.bluetooth.BluetoothReceiver
import com.aiglasses.databinding.ActivityMainBinding
import com.aiglasses.image.Camera
import com.aiglasses.image.HandleImagePath
import com.aiglasses.image.ImageUpload.uploadImage
import com.aiglasses.network.HttpUtil.GLOBAL_URL_TEST
import com.aiglasses.permission.CheckPermission
import com.aiglasses.speaker.Speaker
import com.amap.api.maps.MapView
import com.baidu.speech.EventListener
import com.baidu.speech.EventManager
import com.baidu.speech.EventManagerFactory
import com.baidu.speech.asr.SpeechConstant
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.MainScope
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import org.json.JSONException
import org.json.JSONObject
import java.io.File


class MainActivity : AppCompatActivity(), View.OnClickListener, EventListener,
    ShowMessageUtil.MainActivityExecutor {
    companion object {
        const val CHOOSE_PHOTO = 10001 //标识这是选择图片的这个操作，便于在回调函数中使用
    }

    private lateinit var startBtn: Button
    private lateinit var stopBtn: Button
    private lateinit var killBtn: Button  //退出按钮

    private lateinit var wakeUp: EventManager  //语音唤醒器

    private lateinit var captureBtn: Button  //选择图片按钮
    private lateinit var selectBtn: Button  //选择图片按钮
    private lateinit var uploadBtn: Button  //上传图片按钮

    private lateinit var iv_image: ImageView
    private lateinit var iv_camera: PreviewView

    private lateinit var btn_record_wav: Button
    private lateinit var btn_record_amr: Button
    private lateinit var btn_stop_rec: Button

    private lateinit var mainscope: CoroutineScope
    private lateinit var binding: ActivityMainBinding

    private var txt: TextView? = null
    private var editTextText: EditText? = null
    private var imgFile: File? = null
    private var camera: Camera? = null

    private val recorder = Recorder
    private val speaker = Speaker
    private val map = Map()
    private val navigate = Navigate()


    //获取系统蓝牙适配器 和 接收器
    private lateinit var btAdapter: BluetoothAdapter
    private val btReceiver = BluetoothReceiver()

    private lateinit var btn_stop_navi: Button
    lateinit var mapView: MapView
    lateinit var editText: EditText
    lateinit var recyclerView: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ShowMessageUtil.setAppContext(applicationContext)
        ShowMessageUtil.setMainActivityExecutor(this)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        findViewByIds()
        setOnClickListeners()//点击事件监听
        CheckPermission.checkPermission(this)

        mainscope = MainScope()
        speaker.initSpeaker(mainscope)
        camera = Camera(this)
        wakeUp = EventManagerFactory.create(this, "wp") //语音唤醒器
        wakeUp.registerListener(this)

//        ShowMessageUtil.showMessage("启动！")
        mainscope.launch {
            // do this after check permission
            dealWithBluetooth()
            camera!!.startCamera()
            startWakeUp()
        }
        map.initMap(savedInstanceState, mapView)
        navigate.initNavi(this, mapView)
    }

    override fun onPause() {
        super.onPause()
        mapView.onPause()
    }


    override fun onResume() {
        super.onResume()
        mapView.onResume()
    }

    override fun onSaveInstanceState(outState: Bundle, outPersistentState: PersistableBundle) {
        super.onSaveInstanceState(outState, outPersistentState)
        mapView.onSaveInstanceState(outState)
    }

    override fun onDestroy() {
        super.onDestroy()
        mainscope.cancel()

        // 基于SDK集成4.2 发送取消事件
        wakeUp.send(SpeechConstant.WAKEUP_STOP, "{}", null, 0, 0)
        // 必须与registerListener成对出现，否则可能造成内存泄露
        wakeUp.unregisterListener(this)

        camera?.stopUpload()
        // 必须与registerReceiver成对出现，否则可能造成内存泄露
        unregisterReceiver(btReceiver)

        mapView.onDestroy()

    }

    override fun setTextOnUI(str: String) {
        txt?.text = str
    }

    // 基于sdk集成1.2 自定义输出事件类 EventListener 回调方法
    // 基于SDK集成3.1 开始回调事件
    override fun onEvent(
        name: String,
        params: String?,
        data: ByteArray?,
        offset: Int,
        length: Int
    ) {
//        super.onEvent
        var logTxt = "name: $name"
        if (!params.isNullOrEmpty()) {
            logTxt += " ;params :$params"
            if ("wp.data" == name) {
                try {

                    val word = JSONObject(params).getString("word")

                    //听到唤醒词
                    when (word) {
                        "小智你好" -> {
                            stopWakeUp() // 停止唤醒
                            ShowMessageUtil.showMessage("开始录音")
                            recorder.record(Recorder.FLAG_AMR) // 开始录音
                        }

                        "停止导航" -> {
                            navigate.cancelNavi()
                            ShowMessageUtil.showMessage("导航停止")
                        }

                        else -> {
                            ShowMessageUtil.showMessage(word)
                        }
                    }

                } catch (e: JSONException) {
                    e.printStackTrace()
                }
            }

        }

        Log.d("自定义onEvent", logTxt)
    }


    override fun onRequestPermissionsResult(
        requestCode: Int, permissions: Array<String>, grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        CheckPermission.onRequestPermissionsResult(requestCode, this, grantResults)
    }


    //点击事件
    override fun onClick(view: View) {
        when (view.id) {
            R.id.captureBtn -> captureImage()
            R.id.selectBtn -> selectImage()
            R.id.uploadBtn -> uploadImage(imgFile)  //点击上传图片

            R.id.btn_record_amr -> recorder.record(Recorder.FLAG_AMR)
            R.id.btn_record_wav -> recorder.record(Recorder.FLAG_WAV)

            R.id.btn_stop_rec -> recorder.stop()

            R.id.btn_stop_navi -> navigate.cancelNavi()

            R.id.startBtn -> startWakeUp()
            R.id.stopBtn -> stopWakeUp()
            R.id.killBtn -> killProcess()
        }


    }


    //选择图片后结果显示
    @Deprecated("Deprecated in Java")
    override fun onActivityResult(
        requestCode: Int, resultCode: Int, data: Intent?
    ) {
        super.onActivityResult(requestCode, resultCode, data)

        when (requestCode) {
            CHOOSE_PHOTO -> if (resultCode == RESULT_OK) {
                data?.data?.let { uri ->
                    iv_image.setImageURI(uri)  //显示图片
                    val realPath = HandleImagePath.getRealPath(this, data) //获取真实的图片路径
                    imgFile = realPath?.let { File(it) }
                }
            }
        }
    }

    fun getBinding(): ActivityMainBinding {
        return binding
    }

    private fun killProcess() {
        android.os.Process.killProcess(android.os.Process.myPid())
    }

    @SuppressLint("MissingPermission")
    private fun dealWithBluetooth() {
        if (isOpenBluetooth()) {
//            ShowMessageUtil.showMessage("蓝牙已打开")
//            mBluetoothAdapter = (getSystemService(BLUETOOTH_SERVICE) as BluetoothManager).adapter
            btAdapter = BluetoothAdapter.getDefaultAdapter()
        } else {
            enableBluetooth.launch(Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE))
        }
        btReceiver.setBluetoothAdapter(btAdapter)
        // Register for broadcasts
        val filter = IntentFilter()
        filter.addAction(BluetoothDevice.ACTION_FOUND)
        filter.addAction(BluetoothDevice.ACTION_PAIRING_REQUEST)
        registerReceiver(btReceiver, filter)
        btAdapter.startDiscovery()
    }

    private fun isOpenBluetooth(): Boolean {
        val manager = getSystemService(BLUETOOTH_SERVICE) as BluetoothManager
        val adapter = manager.adapter ?: return false
        return adapter.isEnabled
    }


    //打开蓝牙意图
    private val enableBluetooth =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
            if (it.resultCode == Activity.RESULT_OK) {
                if (isOpenBluetooth()) {
//                mBluetoothAdapter = (getSystemService(BLUETOOTH_SERVICE) as BluetoothManager).adapter
                    btAdapter = BluetoothAdapter.getDefaultAdapter()
//                    ShowMessageUtil.showMessage("蓝牙已打开")
                } else {
                    ShowMessageUtil.showMessage("蓝牙未打开")
                }
            }
        }

    /**
     * 基于SDK集成2.2 发送开始事件
     * 点击开始按钮
     * 测试参数填在这里
     */
    override fun startWakeUp() {
        val params: MutableMap<String?, Any?> = LinkedHashMap()
        val event = SpeechConstant.WAKEUP_START // 替换成测试的event

        // 基于SDK集成2.1 设置识别参数
        params[SpeechConstant.ACCEPT_AUDIO_VOLUME] = false
        params[SpeechConstant.WP_WORDS_FILE] = "assets:///WakeUp.bin"

        val json = JSONObject(params).toString() // 这里可以替换成你需要测试的json
        wakeUp.send(event, json, null, 0, 0)
        Log.d("点击开始按钮", "输入参数：$json")
        ShowMessageUtil.showMessage("开始唤醒")
    }

    /**
     * 点击停止按钮
     * 基于SDK集成4.1 发送停止事件
     */
    private fun stopWakeUp() {
        Log.d("发送停止事件", "停止识别：WAKEUP_STOP")
        wakeUp.send(SpeechConstant.WAKEUP_STOP, null, null, 0, 0)
    }


    //选择图片
    private fun selectImage() {
        val intent = Intent(Intent.ACTION_GET_CONTENT)
        intent.type = "image/*"
        startActivityForResult(intent, CHOOSE_PHOTO)
    }

    private fun captureImage() {
        val img = camera?.takePhoto()
        if (img != null) {
            imgFile = img
        }
    }

    private fun findViewByIds() {
        startBtn = findViewById(R.id.startBtn)
        stopBtn = findViewById(R.id.stopBtn)
        killBtn = findViewById(R.id.killBtn)

        captureBtn = findViewById(R.id.captureBtn)
        selectBtn = findViewById(R.id.selectBtn)
        uploadBtn = findViewById(R.id.uploadBtn)
        iv_image = findViewById(R.id.iv_image) //展示图片
        iv_camera = findViewById(R.id.iv_camera) //展示图片
        btn_record_wav = findViewById(R.id.btn_record_wav)
        btn_record_amr = findViewById(R.id.btn_record_amr)
        btn_stop_rec = findViewById(R.id.btn_stop_rec)
        txt = findViewById(R.id.text)

        editTextText = findViewById(R.id.editTextText)
        editTextText?.setText(GLOBAL_URL_TEST)

        btn_stop_navi = findViewById(R.id.btn_stop_navi)
        mapView = findViewById(R.id.gaode_map)
        editText = findViewById(R.id.search_edit)
        recyclerView = findViewById<View>(R.id.search_rv) as RecyclerView
    }

    private fun setOnClickListeners() {
        captureBtn.setOnClickListener(this)
        selectBtn.setOnClickListener(this)
        uploadBtn.setOnClickListener(this)
        btn_record_wav.setOnClickListener(this)
        btn_record_amr.setOnClickListener(this)
        btn_stop_rec.setOnClickListener(this)

        startBtn.setOnClickListener(this)
        stopBtn.setOnClickListener(this)

        killBtn.setOnClickListener(this)

        //这地方就是下面要讲的搜索导航功能
        btn_stop_navi.setOnClickListener(this)
    }

}




