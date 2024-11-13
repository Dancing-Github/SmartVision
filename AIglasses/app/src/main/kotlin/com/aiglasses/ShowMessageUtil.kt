package com.aiglasses

import android.content.Context
import android.os.Looper
import android.util.Log
import android.widget.Toast

object ShowMessageUtil {
    interface MainActivityExecutor {
        fun startWakeUp()
        fun setTextOnUI(str: String)
    }

    private var applicationContext: Context? = null
    private var mMainActivityExecutor: MainActivityExecutor? = null

    fun setMainActivityExecutor(mainActivityExecutor: MainActivityExecutor?) {
        mMainActivityExecutor = mainActivityExecutor
    }

    fun setAppContext(context: Context) {
        if (context != applicationContext) {
            applicationContext = context
        }
    }

    fun getAppContext(): Context {
        if (applicationContext == null) {
            Log.e("showMessage", "!!!ApplicationContext not set!!!")
            throw Exception("applicationContext==null in ShowMessageUtil.getAppContext()")
        }
        return applicationContext!!
    }

    fun showMessage(msg: String) {
        if (Looper.myLooper() == null) {
            Looper.prepare()
        }
        Toast.makeText(getAppContext(), msg, Toast.LENGTH_SHORT).show()
    }

    fun setText(txt: String) {
        mMainActivityExecutor?.setTextOnUI(txt)
    }

    fun startWakeUp() {
        mMainActivityExecutor?.startWakeUp()
    }
}