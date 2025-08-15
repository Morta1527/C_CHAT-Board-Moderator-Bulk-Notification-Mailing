# C_CHAT-Board-Moderator-Bulk-Notification-Mailing
供C_CHAT板主批量推文及寄信通知

**警告，此程式碼為模擬實際PTT執行情形，強烈不建議輸入隱板資訊避免不必要的外流**


# 環境
使用python環境 3.10.18; win11

# 使用流程1
1. 右上角Code>Downlod ZIP
2. 將config.json資料補齊
3. 寄信範本在"mail_body.txt"，可自行修改
4. 以系統管理員開啟C_CHAT mod.exe
5. 若登入失敗稍等之後再執行，或者將 config.json的login改為true/false --第一個字母一定要小寫

執行後會列出 config.json 裡 符合 BOARD、INDEX_RANGE的文章
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

第一次必須先匯出被檢舉ID。(s=匯出 / n=取消)：
```
輸入s將所有被檢舉之ID匯出至"mail_group.txt"
```
已匯出 ID 名單。
下一步？(y=推文僅[檢舉] / m=寄信 / n=取消)：
```
輸入y會列出即將推文的文章
```
=== 即將推文的文章清單 ===
Index    作者                 時間                        標題
------------------------------------------------------------------------------------------------------------------------
34344    zakokun (雜魚君)      Thu Aug 14 14:05:01 2025  [檢舉] ohyeaaaah 4-11
34345    macaron5566 (暑假中最真道理性的齁粉) Thu Aug 14 14:15:07 2025  [檢舉] A29586380 4-11
34346    macaron5566 (暑假中最真道理性的齁粉) Thu Aug 14 14:26:41 2025  [檢舉] offstage 4-11
34347    macaron5566 (暑假中最真道理性的齁粉) Thu Aug 14 14:29:28 2025  [檢舉] Raphael7725 4-5
34348    PiracyBamboo (學歷多少才當工廠作業員?) Thu Aug 14 14:54:02 2025  [檢舉] KyrieIrving1 4-11
34350    macaron5566 (暑假中最真道理性的齁粉) Thu Aug 14 15:05:22 2025  [檢舉] as8116536 4-11
34351    macaron5566 (暑假中最真道理性的齁粉) Thu Aug 14 15:10:25 2025  [檢舉] c312117 4-11
34352    shirleyEchi (雪米菓)  Thu Aug 14 15:24:56 2025  [檢舉] hugr85 4-11
34353    macaron5566 (暑假中最真道理性的齁粉) Thu Aug 14 15:35:11 2025  [檢舉] q34355997 4-11
34354    macaron5566 (暑假中最真道理性的齁粉) Thu Aug 14 15:56:21 2025  [檢舉] daniel3658 4-11
34355    macaron5566 (暑假中最真道理性的齁粉) Thu Aug 14 16:43:13 2025  [檢舉] canallchen 4-11
34356    shirleyEchi (雪米菓)  Thu Aug 14 16:48:52 2025  [檢舉] s175 4-11
34357    Sugimoto5566 (馬丁)  Thu Aug 14 21:34:43 2025  [檢舉] area223672 4-1
34358    fenix220 (菲)       Thu Aug 14 22:02:08 2025  [檢舉] houjay 4-11
34359    fenix220 (菲)       Thu Aug 14 22:29:14 2025  [檢舉] qw2974 4-11
------------------------------------------------------------------------------------------------------------------------
```
確認OK後再輸入y即開始每3秒推文一次
接著輸入m
```
=== 郵件收件人預覽 ===
  1. A29586380
  2. KyrieIrving1
  3. Raphael7725
  4. area223672
  5. as8116536
  6. c312117
  7. canallchen
  8. daniel3658
  9. houjay
 10. hugr85
 11. offstage
 12. ohyeaaaah
 13. q34355997
 14. qw2974
 15. s175
—— 共 15 位 ——
```
確認ok後會再確認一次郵件內容(由"mail_body.txt"而來)
再輸入y即會每3秒寄一封信並留存 (PyPtt目前不支援群組寄信)

影片：https://youtu.be/D0X-JzqCxas

# 使用流程2
1. 將config.json資料補齊
2. 寄信範本在"mail_body.txt"，可自行修改
3. 執行
```
pip install pyptt
python ptt.py
```
之後同上


