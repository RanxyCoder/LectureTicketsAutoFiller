# LectureTicketsAutoFiller
某某工业大学抢票脚本
# 某东某业大学 抢票脚本

> **说明（代码形式）**  
> 这是一个用于自动打开在线表单、定时/立即填写并提交的学习用脚本。仅供学习参考，使用风险自负 —— 出事儿概不负责。

---

## 功能
- 支持 Chrome（`browser=0`）与 Edge（`browser=1`）两种浏览器驱动。
- 支持定时抢填（传 `pt=(年,月,日,时,分,秒)`）或立即执行（传 `pt=None`）。
- 按页面中 `textarea[@placeholder="请输入"]` 的顺序填写内容。
- 自动点击页面上的 `提交` 按钮并尝试点击 `确认`。

---

## 注意（重要）
- 脚本**严格依赖**页面中 `placeholder="请输入"` 的 `textarea` 定位与顺序。若页面改动（例如 placeholder 文案、按钮文案或 DOM 结构变化），脚本可能失效或填错位置。  
- 请仅在合法授权、合规场景下使用，勿用于破坏、刷票等违法用途。  
- 有能力者请根据实际页面自行修改选择器与等待逻辑以提高稳健性。  

---

## 依赖
- Python 3.8+
- selenium
- 对应浏览器的 WebDriver（ChromeDriver / EdgeDriver），版本需与浏览器匹配并在 PATH 中。

安装 selenium：
```bash
pip install selenium

## 有空可能会更新其他的平台的。
