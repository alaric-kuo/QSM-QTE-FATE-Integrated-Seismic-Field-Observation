# QSM–QTE–FATE 整合式地震場觀測

## NEES-2011-1076－正式發布版 V12.2

[English](README.md)

**作者與理論提出者：** Dr. Han-Jung (Alaric) Kuo（郭瀚嶸 博士）  
**所屬機構：** A&J Management Consulting Limited Company（瀚菱管理顧問有限公司）  
**數值引擎：** V12.2  
**文件版本：** V12.2

> **一條連續的理論鏈、三段可執行觀測方法，以及完整保留的物理證據紀錄。**

```text
RPG → QSM → QTE → FATE
```

本 Repository 將量子結構力學（QSM）、量子拓樸快遞方法（QTE），以及碎形生機拓樸演化論（FATE）的第一個營運層，應用於 NEES-2011-1076 三層鋼構架實驗的四組既有紀錄。

本研究提出的工程問題很直接：

> **當地震運動進入結構後，能勢狀態如何沿著結構關係演化；空間拓樸如何組織這個演化；而當實測結構狀態持續回到場中，又會顯化出哪些路徑、目標命中、作功與反應證據？**

V12.2 依照原本應有的方法順序呈現：

```text
QSM → QTE → FATE
```

先前五組探針並列的公開呈現方式已不再使用。邊流、路徑主導、目標態命中、與作功相容的量、加速度—位移作功迴圈代理，以及後續位移反應仍完整保留，因為它們是彼此不同的物理觀測量，並非額外演算法，也不是敏感度分析組別。

---

# 1. 從這裡開始：本研究在觀測什麼

NEES 既有資料提供各樓層的位移、速度與加速度歷時。傳統分析常把這些量視為彼此分離的反應值；本版本則將它們共同讀取為隨時間演化的結構能勢狀態，追蹤從外部激振、關係與空間演化，到感測器持續進場後的目標命中、路徑集中、與作功相容的顯化，以及後續位移反應。

整體觀測鏈可以寫成：

```text
地震能勢輸入
→ QSM 關係型能勢狀態演化
→ QTE 空間拓樸路徑演化
→ FATE 感測驅動的 Aware_power
→ 路徑、目標命中、作功代理與反應證據
```

## 1.1 V12.2 改變了什麼

V12.2 將原本平行探針的呈現方式，改成三個依序接收不同資訊的方法階段：

| 階段 | 算符與資訊狀態 | 目前工程角色 |
|---|---|---|
| **QSM** | 零對角哈密頓量，`H_QSM = −W`；固定關係通道；僅邊界輸入；不進行持續樓層狀態同化 | 建立輸入驅動的關係型能勢狀態基線 |
| **QTE** | 拉普拉斯哈密頓量，`H_QTE = L(W)`；動態路徑；僅邊界輸入；無持續反應回饋 | 恢復空間拓樸，觀測路徑權重與邊流演化 |
| **FATE** | 拉普拉斯動態路徑，加上三樓層狀態持續同化與反應回饋 | 形成感測驅動的 `Aware_power`，包含目標命中、殘差、路徑、邊流、作功顯化與反應 |

三個階段具有先後關係，接收的資訊也不同。因此，它們的相關係數不能被誤讀為三個互相競爭的預測模型排行榜。每一階段所呈現的是：當新的結構資訊進入演化後，哪些物理狀態開始變得可觀測。

## 1.2 四組紀錄顯示了什麼

在同一套、未因案例而調整的數值設定下，反覆出現四項觀測。

第一，四個案例由 QSM 進入 QTE 後，絕對值包絡對齊都提高。這表示在持續感測尚未進場之前，拉普拉斯空間組織比零對角關係基線保留了更多事件包絡。

第二，具有直接位移、速度與加速度通道的 Kobe 0.35 半主動控制與 Morgan Hill 1.00 被動控制關閉案例，在 FATE 階段呈現高度單步對齊。兩者的平均帶正負號相關係數分別為 $0.656$ 與 $0.753$，平均絕對值包絡相關係數分別為 $0.918$ 與 $0.952$。

第三，四個 FATE 案例皆形成正向的 `1F–2F` 路徑指示，而 QSM 與 QTE 在僅邊界輸入時維持接近均分。感測驅動後的演化歷程並不相同：Kobe 維持強烈集中；Morgan Hill 先集中再重新分配；El Centro uncontrolled 維持一段集中後部分回復；El Centro passive-off 則在中段出現較急遽的轉換。

第四，兩個 El Centro 案例保留了混合訊號語意：1F 為相對位移，2F 與 3F 為絕對位移；速度由位移數值微分取得，加速度則為直接量測。其上層樓 FATE 對齊較弱，被保留為資料生產鏈的證據，而非被濾除。

## 1.3 RPG、QSM、QTE 與 FATE 各自貢獻什麼

| 理論層 | 科學角色 | V12.2 可執行位置 |
|---|---|---|
| **RPG** | 提供 `a·v` 作為直接可計算的單位質量功率表達，以及質量邊界語言 | 由實測運動形成帶正負號、經質量正規化且與作功相容的能勢輸入 |
| **QSM** | 透過非對角哈密頓關係演化結構能勢狀態 | 執行 `H = −W` 的零對角邊界輸入階段 |
| **QTE** | 編譯觀點、拓樸、通道、演化、顯影與行動 | 執行樓層域拉普拉斯階段，觀測動態路徑與邊流 |
| **FATE** | 將場延伸為 `Aware_power → Alert_control → Alive_evolve` | 目前到達感測驅動的 `Aware_power`；警戒、介入與介入後再演化仍待完成 |

**理論順序：** RPG → QSM → QTE → FATE

**可執行順序：** 實測樓層運動 → QSM → QTE → FATE

## 1.4 如何閱讀本 Repository

第一次閱讀時，可先讀第 1、2 與第 11 章，掌握研究問題、方法架構與跨案例主要發現。

若要理解理論與數學架構，可閱讀第 3 至第 7 章。

若要理解實際程式如何對應理論，可閱讀第 4.5 至第 6.3 節，以及第 8 至第 10 章。

完整個案證據位於 [`cases/`](cases/) 各資料夾內的 README；四案例綜整則位於 [`cross_case/README.md`](cross_case/README.md)。

重現、品質保證與版本連續性，可配合第 13 至第 16 章、[`QA_REGRESSION.md`](QA_REGRESSION.md)、[`CHANGELOG.md`](CHANGELOG.md) 與 [`SHA256SUMS.txt`](SHA256SUMS.txt) 閱讀。

---

# 2. 理論階層與目前實作範圍

目前觀測空間包含三個樓層節點與兩條樓層間路徑：

```text
[1F] —— w12 —— [2F] —— w23 —— [3F]
```

加權鄰接矩陣為：

$$
W= \begin{bmatrix} 0 & w_{12} & 0 \\ w_{12} & 0 & w_{23} \\ 0 & w_{23} & 0 \end{bmatrix}
$$

路徑權重滿足：

$$
w_{12}(t)+w_{23}(t)=2
$$

這是既有樓層紀錄目前可以支持的觀測解析度。若要進入構件、接頭、裝置與邊界層級，必須建立對應的 BIM／IFC 或經確認的竣工圖譜。

| 理論層 | 理論角色 | V12.2 實作 | 目前邊界 |
|---|---|---|---|
| **RPG** | 單位質量功率與質量邊界語言 | 使用加速度與速度形成 `a·v` | 未取得實體樓層質量，因此不宣稱絕對瓦特 |
| **QSM** | 非對角哈密頓能勢狀態演化 | 零對角 `H = −W`、固定路徑、邊界輸入 | 本階段不進行樓層狀態持續同化 |
| **QTE** | 空間拓樸與場顯影 | 拉普拉斯 `H = L(W)`、動態路徑與邊流 | 目前 NEES 實作尚未硬輸入結構參數背景場對角項 |
| **FATE** | 活的感測、治理、介入與再演化 | 到達感測驅動的 `Aware_power` | `Alert_control` 與 `Alive_evolve` 尚未執行 |

完整 QTE 場驅動哈密頓量的目標形式為：

$$
H_{\mathrm{field}} = \kappa L_{\mathrm{geo}}(W) + \alpha_v\,\mathrm{diag}\!\left(V_{\mathrm{bg}}\right)
$$

V12.2 在樓層域解析度下執行第一項。背景場 $V_{\mathrm{bg}}$ 尚未由實體質量、剛度、阻尼、材料容量、接頭、裝置、損傷狀態與經確認的邊界條件建立。

---

# 3. 共鳴能勢梯度理論的輸入語言

理論系譜由 RPG 的質量生滅方程式開始：

$$
\frac{1}{m}\frac{dm}{dt} = \frac{a\cdot v}{c^2}
$$

局部單位質量功率表達為：

$$
P_u(t)=a(t)\cdot v(t)
$$

在工程尺度下：

$$
\frac{P}{m}=a\cdot v
$$

NEES 紀錄並未提供將每一樓層通道轉換為絕對瓦特所需的實體樓層質量，因此 V12.2 直接使用 $a\cdot v$ 作為經質量正規化的能勢狀態量，並保留其與作功相容的關係：

$$
\frac{dW}{m} \approx a\cdot du = a\cdot v\,dt
$$

程式保留帶正負號的 $a\cdot v$ 歷程、絕對值包絡、帶正負號與絕對值的累積作功相容量，以及演化狀態與實測狀態之間具相位敏感性的比較。

此處的 $a\cdot v$ 並非任意選取的工程入口；在現有量測邊界下，它是 RPG 能勢關係的直接可計算表達。

與傳統結構動力學的橋接始於：

$$
m\ddot{x}+c\dot{x}+kx=f(t)
$$

乘上速度後得到：

$$
m\ddot{x}\dot{x} + c\dot{x}^{2} + kx\dot{x} = f(t)\dot{x}
$$

這是動能變化、阻尼耗散、彈性儲能與外部輸入功率之間的瞬時平衡。每一個案例皆保留 `17_force_displacement_work_loop_proxy.png`，作為傳統結構力學進入更廣義能勢狀態解讀的入口。

---

# 4. 量子結構力學（Quantum Structural Mechanics）

## 4.1 從資產剛度到能勢通道

傳統結構力學寫成：

$$
F=Kx
$$

QSM 將剛度矩陣同時重新理解為抵抗資產與結構耦合圖。拔除對角線上的自體勢能井後，非對角傳遞關係得以顯影：

```text
剛度／耦合矩陣
→ 拔除對角自體勢能井
→ 保留非對角關係
→ 形成哈密頓能勢通道
→ 載入外部能勢狀態
→ 演化結構波函數
```

通道係數 $\gamma_{ij}$ 表示能勢在節點 $i$ 與 $j$ 之間通過的能力。通道縮窄、損傷、阻塞或裝置作用，都會改變 $\gamma_{ij}$ 並使演化中的狀態重新分流。

## 4.2 哈密頓能勢轉換算符

QSM 從哈密頓演化方程出發：

$$
i\hbar\frac{d}{dt}\lvert\Psi(t)\rangle = \hat{H}\lvert\Psi(t)\rangle
$$

QSM 定義哈密頓能勢轉換算符：

$$
\hat{H}_{p} = -i\left(\frac{\hat{H}}{\hbar}\right)
$$

因此結構能勢狀態滿足：

$$
\frac{d}{dt}\lvert\Psi(t)\rangle = \hat{H}_{p}\lvert\Psi(t)\rangle
$$

其形式演化為：

$$
\lvert\Psi(t)\rangle = e^{\hat{H}_{p}t}\lvert\Psi(0)\rangle
$$

各物件的角色彼此不同：

| 物件 | 意義 |
|---|---|
| `Ĥ` | 結構通道法則的哈密頓描述 |
| `Ĥ_p` | 哈密頓能勢轉換算符 |
| `Ψ(t)`（ket 狀態） | 持續演化的結構能勢狀態 |
| `exp(Ĥ_p t)` | 狀態演化算子 |

## 4.3 QSM 核心能勢方程式與顯化

QSM 的核心能勢顯化方程式為：

$$
P(t) = (a\cdot v)\,\hat{H}_{p}\lvert\Psi(t)\rangle
$$

若寫成空間狀態：

$$
P(x,t) = (a\cdot v)\,\hat{H}_{p}\lvert\Psi(x,t)\rangle
$$

三個因子的角色如下：

| QSM 物件 | 角色 |
|---|---|
| `a·v` | 直接動態能勢輸入，也是單位質量功率尺度 |
| `Ĥ_p` | 能勢通過結構通道時的轉換 |
| `Ψ(t)`（ket 狀態） | 持續演化的結構能勢狀態 |

實驗應用可寫成：

$$
P(t) \sim P_{\mathrm{input}}(t)\,\hat{H}_{p}\lvert\Psi(t)\rangle
$$

本版本以實測 $a(t)\cdot v(t)$ 作為 $P_{\mathrm{input}}(t)$ 的直接一階基礎。

## 4.4 保真度作為目標態命中比例

QSM 透過保真度觀測演化中的狀態命中了何處：

$$
\mathrm{Fid}(t) = \left\lvert \langle\Psi_{\mathrm{target}}\vert\Psi(t)\rangle \right\rvert^2
$$

當目標縮減為節點 $n$ 時：

$$
\mathrm{Fid}^{(n)}(t) = \lvert\Psi_n(t)\rvert^2
$$

目標態命中能勢表示為：

$$
P_{\mathrm{real}}^{\mathrm{target}}(t) \sim P_{\mathrm{input}}(t)\, \mathrm{Fid}^{\mathrm{target}}(t)
$$

累積目標命中等效作功為：

$$
W_{\mathrm{hit}}^{\mathrm{target}}(T) = \int_0^T P_{\mathrm{input}}(t)\, \mathrm{Fid}^{\mathrm{target}}(t) \,dt
$$

這組方程清楚分開輸入尺度、狀態演化與目標命中。

## 4.5 QSM 理論與 V12.2 程式碼的精確對應

程式將零對角 QSM 矩陣建構為：

```python
H = -W
```

對實對稱的 $3\times3$ 算符，數值演化為：

```python
evals, evecs = np.linalg.eigh(H)
U = (evecs * np.exp(-1j * evals * dt)) @ evecs.conj().T
```

其數值形式為：

$$
U(\Delta t)=e^{-iH\Delta t}
$$

在正規化單位 $\hbar=1$ 下：

$$
e^{\hat{H}_{p}\Delta t} = e^{-iH\Delta t}
$$

正確對應關係如下：

| 表示層次 | 物件 |
|---|---|
| 理論上的哈密頓通道法則 | `Ĥ` |
| QSM 哈密頓能勢轉換算符 | `Ĥ_p = −i(Ĥ/ℏ)` |
| 程式層級的等效關係矩陣 | `H = -W` |
| 程式層級的單步演化算子 | `U = exp(-iHΔt)` |

V12.2 刻意讓 QSM 不包含持續樓層狀態同化，也不在本階段重寫自適應路徑。它回答一個邊界清楚的問題：

> 在加入空間拓樸與持續感測之前，邊界激振可以透過非對角關係通道攜帶出什麼能勢狀態？

## 4.6 量測驅動的狀態建構

既有紀錄提供 $u$、$v$ 與 $a$，並未直接量測複數波函數。V12.2 將樓層訊號編譯為正規化複數狀態：

```python
energy = (
    v_norm**2
    + (omega_norm * u_norm)**2
    + 0.25 * a_norm**2
    + 1e-12
)
amp = np.sqrt(energy / np.sum(energy, axis=1, keepdims=True))
phase = np.arctan2(omega_norm * u_norm, v_norm)
psi = amp * np.exp(1j * phase)
```

這是讓資料進入 QSM–QTE–FATE 狀態空間的量測編碼，不會取代 $\lvert\Psi(t)\rangle$ 的典範理論意義。

## 4.7 單步演化與目標命中重建

每一時間步的狀態演化為：

```python
psi_prior = normalize_complex(U @ (psi + source_gain * dt * source))
```

接著計算完整狀態保真度與節點保真度：

```python
state_fidelity = abs(np.vdot(psi_meas[k + 1], psi_prior)) ** 2
fid = np.abs(psi_prior) ** 2
```

下一時間步帶正負號的樓層 $a\cdot v$ 顯化重建為：

```python
evolved_av_next[k + 1] = p_total * fid * evolved_sign
```

程式將 $k+1\vert k$ 的演化狀態與 $k+1$ 的實測 $a\cdot v$ 比較。這是單步演化場檢查，並非長時間自由預測。

QSM 與 QTE 皆維持邊界輸入驅動；持續量測修正只在 FATE 階段進行。

## 4.8 QSM 實作狀態

| QSM 元素 | V12.2 狀態 | 目前實作 |
|---|---|---|
| 剛度至通道的本體轉換 | 已於樓層關係層級實作 | 三節點與兩條非對角關係 |
| 零對角通道條件 | 已實作 | `H = −W` |
| 哈密頓狀態演化 | 已數值實作 | `U = exp(−iHΔt)` |
| 結構複數狀態 | 以量測編碼實作 | 由實測或衍生的 `u`、`v` 與實測 `a` 編譯 |
| 目標態保真度 | 已實作 | 完整狀態重疊與節點模平方 |
| 帶正負號的目標命中顯化 | 以作功相容量重建 | 保真度加權的 `a·v` 顯化 |
| 絕對瓦特與焦耳 | 待校準 | 需要實體樓層質量與通道校準 |
| 長時間自主演化 | 待驗證 | 目前為單步比較後進入下一觀測層 |
| 構件層級目標態 | 待提升解析度 | 目前目標為樓層節點 |

---

# 5. 量子拓樸快遞方法（Quantum Topology Express Method）

## 5.1 QTE 方法論主線

QTE 的方法論主線為：

```text
觀點 → 拓樸 → 通道 → 演化 → 顯影 → 行動
```

目標計算資料流為：

$$
R \rightarrow A \rightarrow W \rightarrow L_{\mathrm{geo}} \rightarrow V_{\mathrm{bg}} \rightarrow H \rightarrow \psi(0) \rightarrow \psi(t) \rightarrow \rho(t) \rightarrow \Delta V_{\mathrm{resp}}(t) \rightarrow J(t) \rightarrow \Gamma(t) \rightarrow m(t) \rightarrow M(t)
$$

| 符號 | QTE 意義 |
|---|---|
| `R` | 節點集合 |
| `A` | 鄰接矩陣 |
| `W` | 幾何或通道權重 |
| `L_geo` | 幾何拉普拉斯 |
| `V_bg` | 背景能勢場 |
| `H` | 完整場驅動哈密頓量 |
| `ψ(t)` | 演化中的拓樸場狀態 |
| `ρ(t)` | 能勢密度 |
| `ΔV_resp(t)` | 動態勢差 |
| `J(t)` | 邊流 |
| `Γ(t)` | 顯化速率 |
| `m(t)` | 累積顯化量 |
| `M(t)` | 顯化分數 |

## 5.2 從 QSM 橋接至 QTE

目前樓層域拓樸中：

$$
D_{ii}=\sum_j W_{ij}
$$

$$
L_{\mathrm{geo}}=D-W
$$

V12.2 可執行的 QTE 階段使用：

$$
H_{\mathrm{QTE}}=L(W)
$$

完整場驅動哈密頓量的目標形式為：

$$
H = \kappa L_{\mathrm{geo}} + \alpha_v\,\mathrm{diag}\!\left(V_{\mathrm{bg}}\right)
$$

這個區分非常重要：

- QSM 顯影非對角關係通道；
- QTE 透過拉普拉斯恢復空間對角項；
- 完整竣工 QTE 模型還必須放入實體背景場。

目前 NEES 執行到達純拓樸條件，並未宣稱材料容量、質量、阻尼、損傷、接頭與裝置狀態已經被編入 $V_{\mathrm{bg}}$。

## 5.3 QTE 可觀測量

能勢密度為：

$$
\rho_i(t)=\lvert\psi_i(t)\rvert^2
$$

典範動態勢差為：

$$
\Delta V_{\mathrm{resp}}(t) = -L_{\mathrm{geo}}\rho(t)
$$

邊流為：

$$
J_{ij}(t) = 2\,\mathrm{Im}\!\left( \psi_i^*(t)H_{ij}\psi_j(t) \right)
$$

局部速度場可寫成：

$$
v_i(t) = \frac{\sum_j J_{ij}(t)u_{ij}} {\rho_i(t)+\epsilon}
$$

局部加速度為：

$$
a_i(t) \approx \frac{v_i(t+\Delta t)-v_i(t)}{\Delta t}
$$

局部顯化速率為：

$$
\Gamma_i(t) = \frac{a_i(t)\cdot v_i(t)}{c^2} = \frac{1}{m_i}\frac{dm_i}{dt}
$$

累積顯化量為：

$$
m_i(t) = m_i(0) \exp\!\left( \int_0^t \Gamma_i(\tau)\,d\tau \right)
$$

完整顯化分數可寫成：

$$
M_i(t) = \lambda_1\left\lvert\Delta V_{\mathrm{resp},i}(t)\right\rvert + \lambda_2\max\!\left(\Gamma_i(t),0\right) + \lambda_3\max\!\left(\Delta V_{\mathrm{bg},i},0\right) + \lambda_4\log m_i(t)
$$

V12.2 並未宣稱 $\Gamma$–$m$–$M$ 的完整治理鏈已經完成；目前保留的是三樓層紀錄可以直接支撐的可執行觀測量。

## 5.4 V12.2 已實作的樓層域 QTE

可執行路徑為：

```text
R
→ A
→ W(t)
→ L(W(t))
→ H_QTE(t)
→ ψ(t)
→ ρ(t)
→ J12(t), J23(t)
→ w12(t), w23(t)
→ 路徑主導 Dp(t)
```

QTE 階段由邊界輸入驅動，啟用動態路徑更新，但不持續同化上層樓的實測狀態。如此可以把空間拓樸組織與後續 FATE 感測層分開觀測。

## 5.5 邊流與路徑顯影

V12.2 計算：

$$
J_{12}(t) = 2\,\mathrm{Im}\!\left( \psi_1^*(t)H_{12}\psi_2(t) \right)
$$

$$
J_{23}(t) = 2\,\mathrm{Im}\!\left( \psi_2^*(t)H_{23}\psi_3(t) \right)
$$

路徑主導指標為：

$$
D_p(t) = \frac{w_{12}(t)-w_{23}(t)} {w_{12}(t)+w_{23}(t)}
$$

| 指標 | 樓層域解讀 |
|---|---|
| `D_p > 0` | `1F–2F` 路徑顯影較強 |
| `D_p < 0` | `2F–3F` 路徑顯影較強 |
| `abs(D_p) ≤ 0.02` | 路徑狀態接近均分 |

路徑權重與邊流是不同的觀測量：

- 路徑權重記錄相對通道狀態的演化；
- 邊流記錄具有相位敏感性的場流動。

V12.2 同時保留兩者的完整歷程、最終值與 RMS 摘要。

## 5.6 QTE 實作狀態

| QTE 元素 | V12.2 狀態 |
|---|---|
| 觀點 | 三樓層觀測觀點 |
| 節點集合 `R` | 已實作 |
| 鄰接矩陣 `A` | 已實作 |
| 動態權重 `W(t)` | 已實作 |
| 拉普拉斯 `L(W)` | 已實作 |
| 邊界驅動的拓樸演化 | 已實作 |
| 複數狀態演化 | 已實作 |
| 密度／保真度 `ρ_i = abs(ψ_i)²` | 已實作 |
| 邊流 `J_12`、`J_23` | 已實作 |
| 路徑權重與主導指標 | 已實作 |
| 實體背景場 `V_bg` | 尚未實作 |
| 完整竣工場驅動哈密頓量 | 尚未實作 |
| 典範 `ΔV_resp` 直接場輸出 | 尚未實作 |
| 顯化速率 `Γ` | 尚未實作 |
| 累積顯化量 `m` | 尚未實作 |
| 治理分數 `M` | 尚未實作 |
| BIM／IFC 構件層級拓樸 | 尚未實作 |

---

# 6. 碎形生機拓樸演化論（Fractal Alive Topology Evolution）

## 6.1 核心方程

FATE 為：

$$
\mathrm{F.A.T.E.} = \mathrm{Aware}_{\mathrm{power}} \cdot \mathrm{Alert}_{\mathrm{control}} \cdot \mathrm{Alive}_{\mathrm{evolve}}
$$

工程方法鏈為：

```text
感知能勢波動路徑
→ 警戒控制致命拓樸
→ 存活演化開放耗散
```

| FATE 層 | 工程角色 | V12.2 狀態 |
|---|---|---|
| `Aware_power` | 讀取輸入狀態、內部場、目標命中、路徑、作功顯化、殘差、反應與資料來源 | 已於樓層域觀測層實作 |
| `Alert_control` | 建立治理門檻並輸出實體介入 | 尚未實作 |
| `Alive_evolve` | 改寫場與算符，再驗證介入後狀態 | 尚未實作 |

## 6.2 V12.2 的感測驅動 `Aware_power`

FATE 持續將三樓層實測狀態送回演化場：

```text
k 時刻實測狀態
→ 建立或修正 Ψ(k)
→ 演化至 k+1|k
→ 與 k+1 實測狀態比較
→ 同化殘差
→ 更新拓樸路徑觀測量
→ 進入下一時間步
```

量測修正為：

```python
residual_full = psi_meas[k + 1] - psi_prior
psi = normalize_complex(
    psi_prior + effective_measurement_gain * residual
)
```

FATE 因此建立七個相連的觀測層：

1. **輸入感知**：地震輸入能勢狀態。
2. **狀態感知**：實測結構耦合複數狀態。
3. **目標感知**：完整狀態保真度與節點目標命中。
4. **路徑感知**：$w_{12}$、$w_{23}$ 與 $D_p$。
5. **流動感知**：$J_{12}$、$J_{23}$ 與其 RMS 比值。
6. **作功與反應感知**：目標命中作功相容歷程、位移側作功、隱藏作功代理與後續反應包絡。
7. **資料溯源感知**：直接或衍生速度、座標定義、插值、微分、擷取與轉換歷史。

## 6.3 FATE 實作狀態

| FATE 元素 | V12.2 狀態 |
|---|---|
| `Aware_power` | 已實作 |
| 樓層狀態持續同化 | 已實作 |
| 單步先驗與實測比較 | 已實作 |
| 狀態保真度與殘差範數 | 已實作 |
| 目標命中能勢狀態重建 | 以作功相容量實作 |
| 感測驅動路徑演化 | 已實作 |
| 邊流演化 | 已實作 |
| 與作功相容的顯化 | 以案例內正規化證據實作 |
| 後續反應顯化 | 已實作 |
| 資料語意感知 | 已實作 |
| 致命拓樸門檻 | 尚未實作 |
| `Alert_control` | 尚未實作 |
| 實體控制命令 | 尚未實作 |
| 介入後算符改寫 | 尚未實作 |
| `Alive_evolve` 驗證 | 尚未實作 |
| 跨尺度碎形遞迴 | 尚未實作 |

---

# 7. 生命週期部署：設計、竣工與營運

QSM、QTE 與 FATE 是同一條生命週期理論鏈。可用證據會從設計假設，演化成經驗證的實體條件，再進入即時感測。

| 生命週期階段 | 可用證據 | QSM–QTE–FATE 角色 |
|---|---|---|
| **設計** | 幾何、拓樸、設計材料、邊界假設、候選系統與可能地震輸入 | 編譯可能的關係與空間通道；比較集中、阻塞、反射、弱面配置與耗散替代方案 |
| **竣工／試運轉** | 經確認的幾何、斷面、質量、剛度、阻尼、接頭、裝置、測試與邊界 | 由實際建築建立 `V_bg` 與場驅動哈密頓量 |
| **營運** | 感測器、裝置狀態、應變、層間位移、位移、速度、加速度、巡檢、維護與損傷 | 持續更新 `Ψ(t)`、`W(t)`、`V_bg(t)` 與 `H(t)`，將感知連接至介入與再演化 |

## 7.1 設計階段的拓樸與能勢輸入探索

設計鏈為：

```text
候選輸入
→ 幾何與語意關係
→ R
→ A
→ W
→ Lgeo
→ 候選能勢通道
→ 集中、阻塞、反射與耗散
```

QSM 顯影關係型傳遞；QTE 顯化拓樸如何改變可能的演化。這可以支援結構配置、阻尼器位置、隔震策略、弱面治理與可接受局部耗散路徑的決策。

## 7.2 竣工後的場驅動通道

施工完成後，經確認的實體資訊可形成背景場：

$$
H = \kappa L_{\mathrm{geo}} + \alpha_v\,\mathrm{diag}\!\left(V_{\mathrm{bg}}\right)
$$

竣工階段把實際拓樸與實際材料、裝置狀況結合，建立後續感測與劣化判讀的參考場。

## 7.3 營運期間的感測、修正與主動控制

目標營運鏈為：

```text
感測器回傳
→ 狀態與場修正
→ 新一輪 QSM–QTE 演化
→ FATE 感知
→ 治理門檻
→ 介入
→ 實測介入後再演化
```

目前 NEES 版本位於回溯式營運階段觀測：利用既有感測紀錄重建樓層域狀態與路徑演化。設計階段 BIM／IFC 編譯、經確認的竣工場建構，以及即時閉迴路控制，仍是下一階段實作。

---

# 8. V12.2 端到端計算流程

```text
1. 讀取原始 NEES 資料檔。

2. 選取或衍生各樓層位移 u(t)、速度 v(t) 與加速度 a(t)。

3. 形成實測單位質量功率歷程：
   Pu(t) = a(t)·v(t)。

4. 將 u、v、a 編譯為正規化複數量測狀態。

5. 執行 QSM：
   H = -W
   固定關係路徑
   僅邊界輸入。

6. 執行 QTE：
   H = L(W)
   動態路徑
   僅邊界輸入。

7. 執行 FATE：
   H = L(W)
   動態路徑
   樓層狀態持續同化
   反應回饋。

8. 每一階段計算單步演化算子：
   U = exp(-iHΔt)。

9. 將當下狀態演化至 k+1|k。

10. 計算完整狀態保真度與節點保真度。

11. 重建下一時間步帶正負號的樓層 a·v 顯化。

12. 將演化狀態與 k+1 實測 a·v 比較。

13. 在 FATE 階段同化實測狀態殘差。

14. 計算邊流 J12 與 J23。

15. 在啟用動態路徑的階段更新路徑權重。

16. 累積目標命中、帶正負號作功、位移側作功、
    隱藏作功代理與反應包絡證據。

17. 輸出標準摘要、149 欄檢查歷程、報告、圖片、
    執行紀錄與檔案清單。
```

---

# 9. 三段可執行方法與完整物理輸出

## 9.1 方法定義

| 方法 | 矩陣 | 動態路徑 | 反應回饋 | 資訊輸入 |
|---|---|---:|---:|---|
| **QSM** | `H = −W` | 否 | 否 | 僅邊界輸入 |
| **QTE** | `H = L(W)` | 是 | 否 | 僅邊界輸入 |
| **FATE** | `H = L(W)` | 是 | 是 | 樓層狀態持續同化 |

V12.2 不再把 boundary-only、fixed-path、no-feedback 或五組探針敏感度條件，生成為公開方法組別。

## 9.2 每一案例的證據檔案

每一案例皆採用相同檔名與順序：

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

三個波形圖各自對應一個方法，並在同一張圖中呈現三個樓層。其他圖片保持分開，因為它們描述的是不同物理量。

## 9.3 完整歷程紀錄

`03_qsm_qte_fate_full_history.csv` 包含 149 欄，並以最多 3,000 列供 GitHub 檢查。內容包含：

- 實測 $u$、$v$、$a$ 與 $a\cdot v$；
- QSM、QTE 與 FATE 演化狀態；
- 帶正負號與絕對值目標命中；
- 單步殘差；
- 累積作功相容量；
- 位移側作功；
- 隱藏作功代理；
- $w_{12}$、$w_{23}$ 與路徑主導；
- $J_{12}$ 與 $J_{23}$；
- 狀態保真度與殘差範數。

這是檢查用歷程，並非完整原始 NEES 資料的再散布。

---

# 10. 資料集與正式案例

**專案：** NEES-2011-1076  
**名稱：** *RTHS and Shake Table Comparison for Smart Structural Systems*  
**資料集 DOI：** [10.7277/TPS7-V877](https://doi.org/10.7277/TPS7-V877)  
**NSF 計畫：** CMMI-1011534 (NEESR)

| 案例 | 來源檔案 | 訊號條件 | stride 後載入筆數 | 圖片事件視窗 |
|---|---|---|---:|---|
| El Centro 0.50 — uncontrolled | `elcentro_0p50_07312012_unc_donghua_converted.csv` | 1F 相對位移；2F–3F 絕對位移；衍生速度 | 203,578 | 51.152400–165.785600 秒 |
| El Centro 0.50 — passive-off | `elcentro_0p50_07312012_poff_donghua_converted.csv` | 相同混合座標結構；衍生速度 | 117,271 | 1.609550–115.161450 秒 |
| Kobe 0.35 — semi-active | `kobe_035_semi_active_avg_converted.csv` | 三樓層皆有直接解析 `u`、`v`、`a` | 16,287 | 7.597168–31.025879 秒 |
| Morgan Hill 1.00 — passive-off | `morgan_1_p_off_avg_converted.csv` | 三樓層皆有直接解析 `u`、`v`、`a` | 16,202 | 4.754883–16.700195 秒 |

原始 NEES 資料與轉換後來源 CSV 不隨本 Repository 再散布。詳見 [`data/README.md`](data/README.md)。

---

# 11. 跨案例發現

## 11.1 三階段單步觀測對齊

表中依序為平均帶正負號相關係數／平均絕對值包絡相關係數。

| 案例 | QSM | QTE | FATE | QSM→QTE 絕對包絡變化 | QTE→FATE 絕對包絡變化 |
|---|---:|---:|---:|---:|---:|
| El Centro 0.50 — uncontrolled | -0.135 / 0.671 | -0.039 / 0.765 | 0.323 / 0.615 | +0.094 | -0.150 |
| El Centro 0.50 — passive-off | 0.002 / 0.617 | 0.037 / 0.737 | 0.258 / 0.589 | +0.121 | -0.148 |
| Kobe 0.35 — semi-active | 0.065 / 0.582 | -0.016 / 0.677 | **0.656 / 0.918** | +0.095 | +0.242 |
| Morgan Hill 1.00 — passive-off | 0.049 / 0.604 | 0.046 / 0.699 | **0.753 / 0.952** | +0.095 | +0.253 |

![跨案例 QSM–QTE–FATE 三階段對齊](cross_case/03_cross_case_qsm_qte_fate_bar.png)

四個案例由 QSM 進入 QTE 後，絕對值包絡對齊皆提高；帶正負號相關仍接近零，表示僅由邊界輸入驅動的演化，尚不能重建內部各樓層的方向與相位。

直接通道的 Kobe 與 Morgan Hill 在 FATE 階段呈現高度帶正負號與包絡對齊。El Centro 的下降不應被簡化為感測失效；它揭露直接加速度、衍生速度與混合位移座標共同作用的後果。

## 11.2 FATE 三樓層對齊

| 案例 | 1F 帶正負號／絕對值 | 2F 帶正負號／絕對值 | 3F 帶正負號／絕對值 |
|---|---:|---:|---:|
| El Centro 0.50 — uncontrolled | 0.778 / 0.900 | 0.093 / 0.477 | 0.097 / 0.469 |
| El Centro 0.50 — passive-off | 0.680 / 0.799 | 0.053 / 0.501 | 0.040 / 0.468 |
| Kobe 0.35 — semi-active | 0.567 / 0.851 | 0.709 / 0.949 | 0.693 / 0.955 |
| Morgan Hill 1.00 — passive-off | 0.733 / 0.907 | 0.785 / 0.974 | 0.740 / 0.974 |

![跨案例三樓層對齊](cross_case/07_cross_case_three_floor_alignment.png)

直接通道案例在三個樓層皆維持高度對齊；El Centro 案例保留強烈的 1F 對齊，但上層樓較弱，與來源通道的資料語意邊界一致。

## 11.3 感測驅動的路徑顯化

| 案例 | FATE 最終 `D_p` | FATE 平均 `D_p` | FATE 邊流比 `J_12/J_23` | 平均顯化作功比例 | 最大反應樓層 |
|---|---:|---:|---:|---:|---|
| El Centro 0.50 — uncontrolled | 0.140 | 0.435 | 3.763 | 0.507 | 3F |
| El Centro 0.50 — passive-off | 0.150 | 0.210 | 2.010 | 0.555 | 1F |
| Kobe 0.35 — semi-active | **0.543** | 0.368 | **4.392** | **0.611** | 3F |
| Morgan Hill 1.00 — passive-off | 0.079 | 0.205 | 1.368 | 0.552 | 2F |

![跨案例 Edge Current Ratio](cross_case/04_cross_case_edge_current_ratio.png)

![跨案例 FATE 最終路徑主導](cross_case/05_cross_case_fate_path_dominance.png)

在 QSM 與 QTE 的邊界驅動階段，路徑權重維持接近均分。樓層狀態進入 FATE 後，四個案例皆形成正向的 `1F–2F` 指示。

最終值不等於完整歷程：

- Kobe 維持強烈下層介面集中；
- Morgan Hill 中段集中較強，之後回到接近均分；
- El Centro uncontrolled 維持一段集中後於後段部分重新分配；
- El Centro passive-off 在中段出現較急遽轉換，之後再分配。

這是樓層域顯化，尚不是構件層級破壞面的獨立證明。

## 11.4 邊流作為獨立觀測量

路徑主導與邊流彼此相關，但並不相同：

- $D_p$ 描述相對路徑權重狀態；
- $J_{12}/J_{23}$ 描述整個事件期間具有相位敏感性的 RMS 流動集中。

Morgan Hill 清楚呈現此差異：其最終路徑主導不高，但邊流比仍大於一，因為事件中段下層介面承載較多場流動，之後才重新分配。

## 11.5 與作功相容的顯化

![跨案例 FATE 顯化作功比例](cross_case/06_cross_case_fate_manifested_work_ratio.png)

平均顯化作功比例在每一案例內正規化，用於判讀目前作功相容容量中已顯化與未顯化的部分。它不是可直接拿來比較不同地震實體能量百分比的物理量。

目前正規化中 3F 反覆接近上限，被明確報告為實作邊界，而不是已校準的效率。

## 11.6 路徑顯化與後續位移反應是不同觀測層

主導路徑與最大位移反應樓層不必相同：

| 觀測 | 意義 |
|---|---|
| QTE／FATE 路徑顯化 | 演化中的能勢狀態在哪裡集中或通過 |
| 後續位移反應 | 運動在哪裡以幾何形式變得可見 |

本版本同時保留兩者。能勢可以沿某一路徑通過與重新分配，而最大位移不一定出現在同一觀測位置。

## 11.7 與 V11 主結果的連續性

原 V11 的主要感測同化拉普拉斯歷程，直接對應至 V12.2 的 FATE 階段。四個案例中，演化與實測 $a\cdot v$、殘差、目標命中、路徑權重、狀態保真度、位移、帶正負號作功、反應包絡與隱藏作功欄位的最大數值差異皆為零。

V12.2 改變的是方法組織與圖片呈現，並未在未說明的情況下更換保留下來的主要感測驅動結果。

---

# 12. 目前證據與發展邊界

| 理論層 | V12.2 已建立的證據 | 後續發展方向 |
|---|---|---|
| **QSM** | 零對角輸入驅動哈密頓狀態演化、節點保真度與目標命中重建 | 實體校準、長時間自主演化與構件層級目標態 |
| **QTE** | 拉普拉斯樓層拓樸、動態路徑、路徑主導與邊流 | 竣工 `V_bg`、完整場驅動哈密頓量、典範顯化場與經驗證的構件定位 |
| **FATE** | 持續狀態同化、單步感測對齊、殘差、目標命中、路徑、作功代理、反應與資料溯源感知 | 治理門檻、`Alert_control`、實體介入與 `Alive_evolve` |
| **生命週期** | 由既有感測紀錄建立回溯式營運觀測 | 設計拓樸編譯、竣工場建構與即時閉迴路 Digital Twin 營運 |

本版本目前支持：

- 在四組紀錄上可重現地執行 QSM → QTE → FATE；
- 反覆出現的 QSM→QTE 事件包絡組織；
- 兩個直接通道案例中的高度 FATE 對齊；
- El Centro 異質訊號語意的明確顯影；
- 樓層域路徑、邊流、目標命中、作功相容與反應歷程；
- 版本連續性與檔案層級溯源。

本版本尚未建立：

- 絕對瓦特或焦耳；
- 普遍性的結構有效性；
- 經獨立驗證的構件層級損傷定位；
- 完整實體背景場；
- 長時間自由預測；
- 自動控制有效性；
- 介入後的閉迴路再演化。

---

# 13. Repository 結構

```text
QSM-QTE-FATE-Integrated-Seismic-Field-Observation/
├── .gitignore
├── README.md
├── README_ZH-TW.md
├── CITATION.cff
├── CHANGELOG.md
├── OUTPUT_GUIDE.md
├── QA_REGRESSION.md
├── SHA256SUMS.txt
├── requirements.txt
├── code/
│   └── qsm_qte_fate_nees_multicase_release_v12_2.py
├── scripts/
│   ├── run_all_cases_v12_2.ps1
│   ├── run_smoke_test_morgan_v12_2.ps1
│   └── update_sha256_from_git.ps1
├── data/
│   └── README.md
├── cases/
│   ├── el_centro_050_uncontrolled/
│   ├── el_centro_050_passive_off/
│   ├── kobe_035_semi_active/
│   └── morgan_hill_100_passive_off/
├── cross_case/
└── release_logs/
    └── 00_RELEASE_RUN_LOG.txt
```

正式引擎生成：

```text
4 案例 × 20 個生成檔案 = 80
10 個跨案例生成檔案 = 10
1 份發布執行紀錄 = 1
正式生成成果總數 = 91
```

四份個案 README 與一份跨案例 README 另外維護，用於科學解讀。

---

# 14. 重現方式

## 14.1 系統需求

- Python 3.10 以上
- NumPy
- pandas
- Matplotlib

```powershell
conda activate ifcman
pip install -r requirements.txt
```

## 14.2 建議本機結構

```text
<base folder>/
├── QSM-QTE-FATE-Integrated-Seismic-Field-Observation/
│   ├── code/
│   ├── scripts/
│   └── ...
└── Data Source/
    ├── elcentro_0p50_07312012_unc_donghua_converted.csv
    ├── elcentro_0p50_07312012_poff_donghua_converted.csv
    ├── kobe_035_semi_active_avg_converted.csv
    └── morgan_1_p_off_avg_converted.csv
```

## 14.3 以腳本執行

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\run_all_cases_v12_2.ps1
```

預設輸出資料夾建立在 Repository 同層：

```text
outputs_qsm_qte_fate_nees_2011_1076_v12_2
```

## 14.4 直接執行 Python

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

# 15. 正式執行與品質保證

V12.2 正式執行環境為：

```text
24 個邏輯處理器
2 個 CSV 前處理工作程序
8 個平行方法工作程序
12 個方法任務
```

| 階段 | 時間 |
|---|---:|
| 資料前處理 | 3.170 秒 |
| QSM／QTE／FATE 方法執行 | 20.507 秒 |
| 成果生成 | 19.123 秒 |
| 內部總執行時間 | 42.881 秒 |

品質保證確認：

1. V12.2 Python 程式已成功編譯。
2. 每一案例皆生成完整 20 檔證據組。
3. 完整歷程 CSV 包含 149 欄。
4. 四個案例的 V12.1 與 V12.2 歷程最大數值差異為零。
5. V11 保留的主要感測驅動歷程與 V12.2 FATE 對應欄位最大差異為零。

這些檢查建立軟體執行與版本連續性，但不等同於普遍物理有效性的證明。

---

# 16. 引用方式

## 16.1 理論著作

- Kuo, Han-Jung (Alaric). *Quantum Structural Mechanics: From Stiffness Assets to Value Flow.* ResearchGate preprint.  
  DOI: [10.13140/RG.2.2.27121.13928](https://doi.org/10.13140/RG.2.2.27121.13928)

- Kuo, Han-Jung (Alaric). *Quantum Topology Express Method.* ResearchGate preprint.  
  DOI: [10.13140/RG.2.2.22329.12645](https://doi.org/10.13140/RG.2.2.22329.12645)

- Kuo, Han-Jung (Alaric). *Fractal Alive Topology Evolution.* ResearchGate preprint.  
  DOI: [10.13140/RG.2.2.27969.72806](https://doi.org/10.13140/RG.2.2.27969.72806)

## 16.2 實驗資料集

Zhang, J., Wu, B., and Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set]. NEES / DesignSafe Data Depot.  
DOI: [10.7277/TPS7-V877](https://doi.org/10.7277/TPS7-V877)

## 16.3 軟體

Repository 的機器可讀引用資訊收錄於 [`CITATION.cff`](CITATION.cff)。

---

# 17. 研究定位

V12.2 建立一條可重現的實驗橋梁：

```text
RPG 直接可計算的單位質量功率表達
→ QSM 關係型哈密頓演化
→ QTE 空間拓樸路徑演化
→ FATE 感測驅動的能勢感知
```

具有直接通道的 Kobe 與 Morgan Hill 案例，重現高度感測驅動單步對齊。四個 FATE 案例皆形成正向的 `1F–2F` 樓層域指示，同時保留各自不同的形成、集中、轉換、恢復與重新分配歷程。El Centro 紀錄則顯示，訊號座標與衍生歷史本身就是被觀測系統的一部分，而非可任意丟棄的前處理細節。

放回建築生命週期後，同一條理論鏈可以始於設計階段的拓樸編譯，發展為竣工後的場驅動哈密頓量，最後進入營運階段的感測修正 Digital Twin，並連接控制與再演化。

目前版本已完成樓層域 `Aware_power` 觀測紀錄；並未宣稱後續控制與介入後演化已經完成。

---

# 18. 權利與作者資訊

Copyright © 2026 A&J Management Consulting Limited Company. All rights reserved.

本 Repository 以科學檢視、引用與可重現性評估為目的公開。原始 NEES 實驗資料仍由資料提供者持有，並受原始資料來源條款約束。

**理論提出者與通訊作者：** Dr. Han-Jung (Alaric) Kuo（郭瀚嶸 博士）  
**所屬機構：** A&J Management Consulting Limited Company（瀚菱管理顧問有限公司）  
**所在地：** 臺灣
