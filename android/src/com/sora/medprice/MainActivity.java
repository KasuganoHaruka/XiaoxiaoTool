package com.sora.medprice;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;

/**
 * 医疗价格多版本查询 · 安卓 APK（M1 内置数据 + 本地检索）。
 * 纯 WebView 壳：加载 assets/index.html（自包含 Web 应用，内置数据、离线检索、
 * 原文高亮跳页核验、别名 localStorage 持久化）。无网络权限，数据不出端。
 */
public class MainActivity extends Activity {
  private WebView web;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    web = new WebView(this);
    WebSettings s = web.getSettings();
    s.setJavaScriptEnabled(true);          // 应用逻辑
    s.setDomStorageEnabled(true);          // localStorage：用户别名持久化
    s.setDatabaseEnabled(true);
    s.setAllowFileAccess(true);            // 读取内置 assets
    s.setLoadWithOverviewMode(false);
    s.setUseWideViewPort(false);
    s.setBuiltInZoomControls(false);       // 缩放由页面内自行实现（原文核验）
    s.setDisplayZoomControls(false);
    s.setTextZoom(100);
    s.setCacheMode(WebSettings.LOAD_NO_CACHE);

    web.setWebChromeClient(new WebChromeClient());
    web.setOverScrollMode(View.OVER_SCROLL_NEVER);
    setContentView(web);

    web.loadUrl("file:///android_asset/index.html");
  }

  @Override
  public void onBackPressed() {
    if (web != null && web.canGoBack()) {
      web.goBack();
    } else {
      super.onBackPressed();
    }
  }
}
