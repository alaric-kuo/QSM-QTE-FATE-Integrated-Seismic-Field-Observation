# QSM–QTE–FATE 整合式地震場觀測

## NEES-2011-1076－正式發布版 V12.2

[English](README.md)

**作者與理論提出者：** Dr. Han-Jung (Alaric) Kuo（郭瀚嶸 博士）  
**所屬機構：** A&J Management Consulting Limited Company（瀚菱管理顧問有限公司）  
**數值引擎：** V12.2  
**文件版本：** V12.2

> **一條循序方法主鏈，保留完整且彼此獨立的物理觀測。**

```text
RPG → QSM → QTE → FATE
```

本 Repository 將 QSM–QTE–FATE 架構實作於 NEES-2011-1076 三層鋼構實驗的四組既有紀錄，所處理的工程問題是：

> **當地震運動進入結構之後，能勢狀態如何演化、空間路徑如何被組織，而實際量測的結構狀態持續進入觀測後，又會顯化出什麼？**

V12.2 的公開方法只有三段，且具有明確先後關係：

```text
QSM → QTE → FATE
```

過去五組 probe 的平行表達已經移除。邊流、路徑優勢、目標態命中、作功相容代理量、加速度／力－位移迴圈，以及反應顯化仍完整保留，因為它們是不同的物理觀測維度，並非額外演算法，也不是敏感度分析組別。

---

# 一、V12.2 實際執行的三段方法

| 階段 | V12.2 算符與資訊狀態 | 目前角色 |
|---|---|---|
| **QSM** | `H = -W`；對角線歸零；關係通道固定；由邊界輸入驅動 | 讓輸入能勢透過非對角結構關係演化 |
| **QTE** | `H = L(W)`；放回拉普拉斯對角項；路徑動態演化；仍由邊界輸入驅動 | 加入空間拓樸，觀察路徑權重與邊流如何演化 |
| **FATE** | QTE 演化＋三樓層狀態持續同化＋反應回饋 | 形成感測器驅動的 `Aware_power`，觀察路徑、目標命中、作功代理與反應 |

三段方法接收的資訊逐層增加，因此各階段的相關係數**不是三個模型的排行榜**。

目前 QTE 是 NEES 樓層域的**純拓樸實作**。本版本沒有宣稱已經把實體質量、剛度、阻尼、構件能力、接頭、損傷狀態及控制裝置狀態，完整寫入竣工背景場對角項。

完整的場驅動哈密頓量可表示為：

$$
H_{QTE}=\kappa L_{\mathrm{geo}}(W)+\alpha_v\operatorname{diag}(V_{\mathrm{bg}})
$$

V12.2 目前在可取得的三樓層解析度上，執行其中的拉普拉斯拓樸項。

---

# 二、四案例主要結果

## 2.1 三階段單步觀測對齊

下表格式固定為：

```text
平均帶正負號相關／平均絕對值包絡相關
```

| 案例 | QSM | QTE | FATE | QSM→QTE Δabs | QTE→FATE Δabs |
|---|---:|---:|---:|---:|---:|
| El Centro 0.50－無控制 | -0.135 / 0.671 | -0.039 / 0.765 | 0.323 / 0.615 | +0.094 | -0.150 |
| El Centro 0.50－被動控制關閉 | 0.002 / 0.617 | 0.037 / 0.737 | 0.258 / 0.589 | +0.121 | -0.148 |
| Kobe 0.35－半主動控制 | 0.065 / 0.582 | -0.016 / 0.677 | **0.656 / 0.918** | +0.095 | +0.242 |
| Morgan Hill 1.00－被動控制關閉 | 0.049 / 0.604 | 0.046 / 0.699 | **0.753 / 0.952** | +0.095 | +0.253 |

![跨案例 QSM-QTE-FATE 三階段對齊](cross_case/03_cross_case_qsm_qte_fate_bar.png)

四組案例從 QSM 進入 QTE 後，絕對值包絡相關皆提升，增幅約為 `0.094–0.121`。這表示拉普拉斯拓樸在樓層狀態尚未持續同化前，已經對地震事件包絡形成空間組織。但 QSM 與 QTE 的帶正負號相關仍接近零，顯示只靠邊界輸入，尚不足以重建各樓層內部狀態的方向與相位。

Kobe 與 Morgan Hill 的三個樓層皆具有直接解析的位移、速度與加速度通道。當樓層實測狀態持續進入 FATE 後，其平均絕對值包絡相關分別提升至 `0.918` 與 `0.952`。

兩組 El Centro 的 1F 位移為相對座標，2F、3F 位移為絕對座標，速度則由位移微分取得。FATE 讓這組異質資料真正進入場後，平均包絡相關反而下降，但 1F 的帶正負號與包絡對齊仍明顯高於上層。這項差異被保留為**資料語意觀測**，而不是被平均值掩蓋。

## 2.2 FATE 三樓層對齊

| 案例 | 1F signed/abs | 2F signed/abs | 3F signed/abs |
|---|---:|---:|---:|
| El Centro 0.50－無控制 | 0.778 / 0.900 | 0.093 / 0.477 | 0.097 / 0.469 |
| El Centro 0.50－被動控制關閉 | 0.680 / 0.799 | 0.053 / 0.501 | 0.040 / 0.468 |
| Kobe 0.35－半主動控制 | 0.567 / 0.851 | 0.709 / 0.949 | 0.693 / 0.955 |
| Morgan Hill 1.00－被動控制關閉 | 0.733 / 0.907 | 0.785 / 0.974 | 0.740 / 0.974 |

![跨案例三樓層對齊](cross_case/07_cross_case_three_floor_alignment.png)

## 2.3 感測器驅動的路徑顯化

| 案例 | FATE 最終優勢 `D` | FATE 平均 `D` | FATE 最大 `D` | FATE 邊流比 `J12/J23` | 平均顯化作功比 |
|---|---:|---:|---:|---:|---:|
| El Centro 0.50－無控制 | 0.140 | 0.435 | 0.692 | 3.763 | 0.507 |
| El Centro 0.50－被動控制關閉 | 0.150 | 0.210 | 0.421 | 2.010 | 0.555 |
| Kobe 0.35－半主動控制 | **0.543** | 0.368 | 0.619 | **4.392** | **0.611** |
| Morgan Hill 1.00－被動控制關閉 | 0.079 | 0.205 | 0.462 | 1.368 | 0.552 |

![跨案例 Edge Current Ratio](cross_case/04_cross_case_edge_current_ratio.png)

![跨案例 FATE 最終路徑優勢](cross_case/05_cross_case_fate_path_dominance.png)

在只由邊界輸入驅動的 QSM 與 QTE 中，路徑權重及 Edge Current Ratio 均接近等分。當樓層實測狀態進入 FATE 後，四組案例最終皆出現正值 `D`，指向較高權重的 `1F–2F` 路徑，但每一案的時間歷程不同：

- **Kobe：** 下層介面集中最強，且相對持續。
- **Morgan Hill：** 中途曾有較強集中，後續大幅重新分配，最終值低估了歷程中的最大分離。
- **El Centro 無控制：** 中段持續集中，最後部分回復。
- **El Centro 被動控制關閉：** 中段轉換較突然，之後逐步重新分配。

目前的結論是樓層域路徑顯化，尚不能直接宣稱為構件層級損傷面或已經獨立驗證的物理弱面。

## 2.4 作功相容顯化

![跨案例 FATE 顯化作功比例](cross_case/06_cross_case_fate_manifested_work_ratio.png)

作功相容比例是在每一案例內部正規化的代理量，可用來閱讀已顯化部分與未顯化餘裕，不能解讀為不同地震之間可以直接比較的實體能量百分比。目前 3F 重複出現的正規化上限，也被明確記錄為本實作的尺度邊界，並非獨立校準後的物理效率。

---

# 三、理論與工程鏈

## 3.1 RPG：直接可計算的單位質量功率語言

理論系譜由 Resonance Power Gradient Theory 開始：

$$
\frac{1}{m}\frac{dm}{dt}=\frac{a\cdot v}{c^2}
$$

本實驗所使用的工程觀測量為：

$$
\frac{P}{m}=a\cdot v
$$

NEES 資料未提供將各樓層換算為絕對瓦特所需的實體質量，因此 V12.2 保留 `a·v` 作為經質量正規化、且與作功相容的能勢狀態量。它是本方法直接可計算的表達，不只是繪圖方便的代理入口。

與傳統結構動力學的銜接由單自由度方程式開始：

$$
m\ddot{x}+c\dot{x}+kx=f(t)
$$

兩側乘上速度後，可得到動能變化、彈性儲能、阻尼耗散與外部輸入之間的瞬時 Power balance。每個個案保留的 `17_force_displacement_work_loop_proxy.png`，就是把場觀測重新接回傳統加速度／力－位移及作功語言的入口。

## 3.2 QSM：零對角哈密頓能勢狀態演化

QSM 將對角線上的自體勢能井拔除，凸顯非對角結構關係：

$$
H_{QSM}=-W
$$

在正規化單位下，程式透過下式演化複數結構狀態：

$$
U(\Delta t)=e^{-iH\Delta t}
$$

V12.2 的 QSM 階段刻意保持乾淨：

```text
邊界輸入
→ 零對角關係哈密頓量
→ 單步能勢狀態演化
```

它先回答：在尚未加入拉普拉斯空間拓樸及持續感測前，外部輸入能沿既有非對角關係傳遞到什麼程度。

## 3.3 QTE：拉普拉斯空間拓樸路徑演化

QTE 放回拉普拉斯對角項：

$$
L(W)=D(W)-W
$$

目前執行：

$$
H_{QTE}=L(W)
$$

三樓層模型具有兩條可觀測路徑：

```text
[1F] —— w12 —— [2F] —— w23 —— [3F]
```

並維持：

$$
w_{12}+w_{23}=2
$$

路徑優勢定義為：

$$
D_p(t)=\frac{w_{12}(t)-w_{23}(t)}{w_{12}(t)+w_{23}(t)}
$$

邊流則為：

$$
J_{ij}(t)=2\,\operatorname{Im}\left(\psi_i^*(t)H_{ij}\psi_j(t)\right)
$$

V12.2 將路徑權重、路徑優勢與邊流歷程分別保留，使空間演化不會被濃縮成單一最終標籤。

## 3.4 FATE：感測器驅動的持續演化

FATE 不另行創造第四種平行 Hamiltonian，而是讓實際量測狀態持續進入 QSM–QTE 演化鏈：

```text
時間 t 的感測狀態
→ 更新 Ψ(t)
→ 演化拓樸與路徑
→ 觀測目標命中、邊流、作功代理、殘差與反應
→ 同化下一筆量測
```

目前完成的層級為：

```text
Aware_power
```

後續理論順序為：

```text
Aware_power → Alert_control → Alive_evolve
```

V12.2 尚未宣稱已經完成自動警戒門檻、控制介入，以及介入後的閉迴路再演化。

---

# 四、放回建築生命週期

QSM、QTE、FATE 是一條生命週期上的資訊與物理條件逐步增加鏈，而非三個互不相干的軟體模組。

## 設計階段

BIM／IFC 幾何與結構關係可先編譯為節點、鄰接與候選通道。QSM 可凸顯非對角傳輸關係；QTE 可觀察不同拓樸如何允許集中、阻塞、反射與消散。

## 施工、竣工與試運轉階段

實際構件、質量、剛度、阻尼、接頭、裝置、邊界、安裝狀態與試運轉結果，可共同形成背景場 `V_bg`。此時才可建立完整場驅動哈密頓量：

$$
H=\kappa L_{\mathrm{geo}}+\alpha_v\operatorname{diag}(V_{\mathrm{bg}})
$$

## 營運與 Digital Twin

感測器持續更新結構狀態與路徑，FATE 再把能勢感知連接至控制策略、介入及再演化。完整目標鏈為：

```text
BIM／IFC 拓樸
→ 竣工場驅動 Hamiltonian
→ 即時感測
→ Digital Twin 感知
→ 控制策略
→ 介入後實測再演化
```

目前 NEES 版本是在營運階段使用既有感測資料所做的回溯式樓層域觀測。

---

# 五、實驗資料與訊號溯源

| 案例 | 資料檔 | 訊號條件 | stride 後資料列 | 波形事件視窗 |
|---|---|---|---:|---|
| El Centro 0.50－無控制 | `elcentro_0p50_07312012_unc_donghua_converted.csv` | 1F 相對位移；2F–3F 絕對位移；速度衍生 | 203,578 | 51.152400–165.785600 s |
| El Centro 0.50－被動控制關閉 | `elcentro_0p50_07312012_poff_donghua_converted.csv` | 同樣的混合座標；速度衍生 | 117,271 | 1.609550–115.161450 s |
| Kobe 0.35－半主動控制 | `kobe_035_semi_active_avg_converted.csv` | 三樓層皆為直接解析 `u`、`v`、`a` | 16,287 | 7.597168–31.025879 s |
| Morgan Hill 1.00－被動控制關閉 | `morgan_1_p_off_avg_converted.csv` | 三樓層皆為直接解析 `u`、`v`、`a` | 16,202 | 4.754883–16.700195 s |

原始資料：

> Zhang, J., Wu, B., and Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)*. DOI: [10.7277/TPS7-V877](https://doi.org/10.7277/TPS7-V877)

本 Repository 不重新散布 NEES 原始資料與轉換後的來源 CSV。

---

# 六、Repository 閱讀順序

## 跨案例總結

- [`cross_case/README.md`](cross_case/README.md)：四案例科學綜整。
- `01_cross_case_method_summary.csv`：每案、每方法一列。
- `02_cross_case_floor_summary.csv`：每案、每方法、每樓層一列。
- 圖 `03–07`：三階段對齊、邊流、路徑優勢、作功顯化及三樓層比較。

## 個案層級

- [El Centro 0.50－無控制](cases/el_centro_050_uncontrolled/README.md)
- [El Centro 0.50－被動控制關閉](cases/el_centro_050_passive_off/README.md)
- [Kobe 0.35－半主動控制](cases/kobe_035_semi_active/README.md)
- [Morgan Hill 1.00－被動控制關閉](cases/morgan_hill_100_passive_off/README.md)

每個案例使用完全一致的 20 個生成檔案，另加一份敘事 README。

<details>
<summary>每案 V12.2 完整檔名</summary>

```text
01_qsm_qte_fate_method_summary.csv
02_qsm_qte_fate_floor_summary.csv
03_qsm_qte_fate_full_history.csv
04_CASE_REPORT.md
05_release_report.txt
06_qsm_qte_fate_stage_bar.png
07_qsm_three_floor_waveforms.png
08_qte_three_floor_waveforms.png
09_fate_three_floor_waveforms.png
10_qsm_qte_fate_edge_current_ratio.png
11_qte_path_weight_evolution.png
12_fate_sensor_aware_path_evolution.png
13_qte_fate_edge_current_evolution.png
14_qte_fate_path_dominance_evolution.png
15_fate_target_hit_state_awareness.png
16_fate_work_proxy_ratios_by_floor.png
17_force_displacement_work_loop_proxy.png
18_response_manifestation_by_floor.png
19_release_run_log.txt
20_release_file_manifest.json
README.md
```

</details>

`03_qsm_qte_fate_full_history.csv` 具有 149 欄，並下採樣至最多 3,000 列供 GitHub 檢查。內容保留實測通道、三階段演化、殘差、目標命中、累積作功相容量、路徑權重、路徑優勢、邊流、狀態保真度及殘差範數。

---

# 七、重現方式

## 7.1 安裝環境

```powershell
conda activate ifcman
pip install -r requirements.txt
```

目前依賴 NumPy、pandas 與 Matplotlib。

## 7.2 建議本機資料夾結構

```text
<專案總目錄>/
├─ QSM-QTE-FATE-Integrated-Seismic-Field-Observation/
│  ├─ code/
│  ├─ scripts/
│  │  ├─ run_all_cases_v12_2.ps1
│  │  ├─ run_smoke_test_morgan_v12_2.ps1
│  │  └─ update_sha256_from_git.ps1
│  └─ ...
└─ Data Source/
   ├─ elcentro_0p50_07312012_unc_donghua_converted.csv
   ├─ elcentro_0p50_07312012_poff_donghua_converted.csv
   ├─ kobe_035_semi_active_avg_converted.csv
   └─ morgan_1_p_off_avg_converted.csv
```

執行四案：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\run_all_cases_v12_2.ps1
```

成果預設輸出在 Repository 的上一層：

```text
outputs_qsm_qte_fate_nees_2011_1076_v12_2
```

直接執行 Python：

```powershell
python .\code\qsm_qte_fate_nees_multicase_release_v12_2.py `
  --root "D:\path\to\Data Source" `
  --out "D:\path\to\outputs_qsm_qte_fate_nees_2011_1076_v12_2" `
  --stride 5 `
  --workers 8 `
  --prepare-workers 2 `
  --chunk-rows 200000
```

---

# 八、正式執行與品質保證

V12.2 正式版以同一組設定完成四案：

```text
24 個邏輯處理器
2 個 CSV 準備程序
8 個平行方法程序
12 個方法任務
內部總耗時 42.881 秒
```

數值引擎生成：

```text
4 案 × 每案 20 檔 = 80
跨案例 10 檔 = 10
根目錄執行紀錄 = 1
正式生成成果總數 = 91
```

五份敘事 README 另行維護，用於解釋數值與證據邊界。

回歸檢查確認：

- V12.1 與 V12.2 四案的 149 欄歷程完全一致，最大數值差為 `0`。
- V12.2 FATE 的核心歷程，與 V11 原本主要的感測同化 Laplacian 顯化，在已對應的狀態、目標命中、路徑權重、保真度、殘差、位移及 hidden-work 欄位上完全一致，最大數值差為 `0`。
- V12.2 修正的是方法組織與跨案例呈現，沒有在未說明的情況下改動被保留的 FATE 結果。

詳見 [`QA_REGRESSION.md`](QA_REGRESSION.md)。

---

# 九、目前證據邊界

## 本可執行版本目前支持

- 四案例皆可執行乾淨的 QSM 零對角輸入驅動基線。
- 拉普拉斯拓樸在四案皆帶來可重複的 QSM→QTE 包絡組織。
- 兩組直接通道案例在 FATE 感測同化後，重複出現高度單步對齊。
- El Centro 的混合座標與衍生速度限制被明確顯化，而非被資料清理掩蓋。
- 樓層域路徑權重、邊流、目標命中、作功相容與反應歷程可完整追溯。
- 四案在 FATE 皆出現 `1F–2F` 路徑指示，但保留不同的形成、集中、回復與重新分配歷程。
- 程式、固定參數、來源溯源、紀錄、摘要、圖像與 manifest 可重現。

## 尚未建立

- 在缺少實體樓層質量與通道校準下的絕對瓦特或焦耳。
- 構件層級損傷定位或已獨立驗證的弱面判定。
- 完整竣工 `V_bg` 場驅動 Hamiltonian。
- 不進行量測更新的長時間自主演化。
- 自動化 `Alert_control` 判準。
- 閉迴路控制介入及 `Alive_evolve` 驗證。
- 超出目前實驗紀錄的普遍結構有效性。

---

# 十、版本與引用

V12.2 將過去五組 probe 的公開表達，修正為原本的循序方法主鏈，同時保留所有彼此獨立的物理觀測。詳見 [`CHANGELOG.md`](CHANGELOG.md)。

引用本成果時，請同時引用原始資料集、理論成果與本軟體版本。機器可讀的引用資訊位於 [`CITATION.cff`](CITATION.cff)。

理論文獻：

- Kuo, H.-J. *Quantum Structural Mechanics: From Stiffness Assets to Value Flow*. DOI: [10.13140/RG.2.2.27121.13928](https://doi.org/10.13140/RG.2.2.27121.13928)
- Kuo, H.-J. *Quantum Topology Express Method*. DOI: [10.13140/RG.2.2.22329.12645](https://doi.org/10.13140/RG.2.2.22329.12645)
- Kuo, H.-J. *Fractal Alive Topology Evolution*. DOI: [10.13140/RG.2.2.27969.72806](https://doi.org/10.13140/RG.2.2.27969.72806)

完整檔案雜湊列於 [`SHA256SUMS.txt`](SHA256SUMS.txt)。
