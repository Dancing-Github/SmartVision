package com.aiglasses.audio

import android.content.Context
import android.content.res.Resources
import com.aiglasses.R

object ErrorCode {
    const val SUCCESS = 1000
    const val E_NOSDCARD = 1001
    const val E_STATE_RECODING = 1002
    const val E_UNKOWN = 1003

    @Throws(Resources.NotFoundException::class)
    fun getErrorInfo(vContext: Context, vType: Int): String {
        return when (vType) {
            SUCCESS -> "success"
            E_NOSDCARD -> vContext.resources.getString(R.string.error_no_sdcard)
            E_STATE_RECODING -> vContext.resources.getString(R.string.error_state_record)
            E_UNKOWN -> vContext.resources.getString(R.string.error_unknown)
            else -> vContext.resources.getString(R.string.error_unknown)
        }
    }
}
