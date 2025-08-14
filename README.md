# C_CHAT-Board-Moderator-Bulk-Notification-Mailing
供C_CHAT板主批量推文及寄信通知

<code style="color : red">警告</code>

# 環境
使用python環境 3.10.18; win11

# 使用流程
1. 將config.json資料補齊
2. 寄信範本在"mail_body.txt"，可自行修改
3. 執行
```
python ptt.py
```
若登入失敗稍等之後再執行，或者將 line 257的 kick_other_session=True改為False

4.執行後會列出 config.json 裡 符合 BOARD、INDEX_RANGE的文章
```
看板：C_ChatBM，共 16 筆
Index    作者               時間                       標題

34344    zakokun (雜魚君)    Thu Aug 14 14:05:01 20…  [檢舉] ohyeaaaah 4-11
34345    macaron5566 (暑…  Thu Aug 14 14:15:07 20…  [檢舉] A29586380 4-11
34346    macaron5566 (暑…  Thu Aug 14 14:26:41 20…  [檢舉] offstage 4-11
34347    macaron5566 (暑…  Thu Aug 14 14:29:28 20…  [檢舉] Raphael7725 4-5
34348    PiracyBamboo (…  Thu Aug 14 14:54:02 20…  [檢舉] KyrieIrving1 4-11
34349    gcobc12632 (Te…  Thu Aug 14 14:57:37 20…  [問題] 關於4-10的判定標準
34350    macaron5566 (暑…  Thu Aug 14 15:05:22 20…  [檢舉] as8116536 4-11
34351    macaron5566 (暑…  Thu Aug 14 15:10:25 20…  [檢舉] c312117 4-11
34352    shirleyEchi (雪…  Thu Aug 14 15:24:56 20…  [檢舉] hugr85 4-11
34353    macaron5566 (暑…  Thu Aug 14 15:35:11 20…  [檢舉] q34355997 4-11
34354    macaron5566 (暑…  Thu Aug 14 15:56:21 20…  [檢舉] daniel3658 4-11
34355    macaron5566 (暑…  Thu Aug 14 16:43:13 20…  [檢舉] canallchen 4-11
34356    shirleyEchi (雪…  Thu Aug 14 16:48:52 20…  [檢舉] s175 4-11
34357    Sugimoto5566 (…  Thu Aug 14 21:34:43 20…  [檢舉] area223672 4-1
34358    fenix220 (菲)     Thu Aug 14 22:02:08 20…  [檢舉] houjay 4-11
34359    fenix220 (菲)     Thu Aug 14 22:29:14 20…  [檢舉] qw2974 4-11

以上為將要推文的文章清單，是否繼續執行推文？(y=推文 / n=取消 / s=匯出被檢舉ID)：
```
輸入y將
