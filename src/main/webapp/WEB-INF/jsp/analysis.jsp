<%@ page contentType="text/html;charset=UTF-8" %>
<html>
<head>
    <title>问卷解析结果</title>
    <!-- 标签页图标 -->
    <link rel="icon" href="https://java------------ai.oss-cn-beijing.aliyuncs.com/2025/12/1.jpg" type="image/jpg">
    <!-- 引入Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- 引入Font Awesome图标 -->
    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <style>
        /* 自定义样式 */
        body {
            background: linear-gradient(135deg, #87CEEB 0%, #98FB98 100%);
            min-height: 100vh;
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
        }

        .card-container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            border-radius: 12px;
            overflow: hidden;
            background-image: url('https://java------------ai.oss-cn-beijing.aliyuncs.com/2025/12/1.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            position: relative;
        }

        .card-header {
            background: transparent;
            padding: 25px;
            text-align: center;
        }

        .card-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
            color: #2D3748;
            text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8), 0 -1px 0 rgba(255, 255, 255, 0.5);
        }

        .card-body {
            padding: 25px;
            background-color: rgba(255, 255, 255, 0.95);
        }

        /* 返回按钮 */
        .back-btn {
            position: absolute;
            top: 15px;
            left: 15px;
            padding: 5px 10px;
            background: rgba(158, 158, 158, 0.8);
            border: none;
            font-size: 12px;
            border-radius: 4px;
            cursor: pointer;
            z-index: 10;
            color: white;
        }
        
        .back-btn:hover {
            background: rgba(117, 117, 117, 0.95);
        }

        /* 加载动画 */
        .loading-container {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .loading-spinner {
            border: 3px solid rgba(66, 165, 245, 0.3);
            border-top: 3px solid #42a5f5;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }

        /* 题目容器 */
        .question-container {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }

        .question-header {
            font-weight: bold;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }

        .question-number {
            background-color: #42a5f5;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            margin-right: 10px;
            font-size: 14px;
        }

        .question-type {
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-right: 10px;
        }

        .question-content {
            margin-bottom: 15px;
            font-size: 15px;
            color: #333;
        }

        /* 选项容器 */
        .options-container {
            margin-bottom: 15px;
        }

        /* 单选/多选题选项 */
        .option-item {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }

        .option-text {
            flex: 1;
            margin-right: 10px;
        }

        .probability-input {
            width: 80px;
            margin-right: 5px;
            font-size: 14px;
            padding: 5px;
        }

        /* 填空题 */
        .fill-blank-container {
            margin-bottom: 10px;
        }

        /* 矩阵题 */
        .matrix-container {
            overflow-x: auto;
        }

        .matrix-table {
            border-collapse: collapse;
            width: 100%;
        }

        .matrix-table th,
        .matrix-table td {
            border: 1px solid #dee2e6;
            padding: 8px;
            text-align: center;
        }

        .matrix-table th {
            background-color: #e9ecef;
            font-weight: bold;
        }

        /* 量表题 */
        .scale-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }

        .scale-labels {
            display: flex;
            align-items: center;
            width: 100%;
            margin: 0 10px;
        }

        .scale-label {
            flex: 1;
            text-align: center;
            font-size: 12px;
        }

        /* 操作按钮 */
        .btn-sm {
            padding: 2px 8px;
            font-size: 12px;
            min-width: 50px;
        }
        
        /* 文本答案弹窗按钮 */
        .modal-content button {
            margin-right: 5px;
        }
        
        /* 确保输入框和百分号在同一行 */
        .option-item div {
            display: flex;
            align-items: center;
        }

        /* 文本答案配置弹窗 */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.4);
        }

        .modal-content {
            background-color: #fefefe;
            margin: 15% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 400px;
            border-radius: 8px;
        }

        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
        }

        .close:hover,
        .close:focus {
            color: black;
            text-decoration: none;
            cursor: pointer;
        }

        .answer-item {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }

        .answer-text {
            flex: 1;
            margin-right: 10px;
        }

        /* 刷问卷按钮 */
        .btn-success {
            background: rgba(76, 175, 80, 0.9);
            border: none;
            border-radius: 6px;
            padding: 11px 20px;
            font-size: 14px;
            font-weight: 600;
            width: 100%;
            color: white;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-success:hover {
            background: rgba(67, 160, 71, 0.95);
            box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
        }
    </style>
</head>
<body>
<div class="card-container">
    <!-- 卡片头部 -->
    <div class="card-header">
        <div class="card-title">问卷解析结果</div>
    </div>

    <!-- 卡片内容 -->
    <div class="card-body">
        <button type="button" class="back-btn" onclick="confirmBack()">
            <i class="fa fa-arrow-left" aria-hidden="true"></i> 返回首页
        </button>

        <!-- 系统配置区域 -->
        <div class="system-config" style="margin-top: 20px; padding: 15px; background-color: #f0f8ff; border-radius: 8px; border: 1px solid #b3d9ff; display: none;">
            <h5 style="margin-bottom: 15px; color: #0066cc;">系统配置</h5>
            <div style="display: flex; flex-wrap: wrap; gap: 15px; align-items: center;">
                <!-- 目标份数 -->
                <div style="display: flex; align-items: center; margin-right: 20px;">
                    <label for="targetCount" style="margin-right: 10px; font-weight: bold;">目标份数:</label>
                    <input type="number" id="targetCount" class="form-control" min="10" max="200" value="10" style="width: 100px; margin-right: 10px;">
                    <span style="color: #666;">份</span>
                </div>
                
                <!-- 系统使用须知按钮 -->
                <button type="button" class="btn btn-sm btn-primary" id="usageIntroBtn">
                    <i class="fa fa-book" aria-hidden="true"></i> 系统使用须知
                </button>
                
                <!-- 一键随机概率按钮 -->
                <button type="button" class="btn btn-sm btn-warning" id="randomProbBtn">
                    <i class="fa fa-random" aria-hidden="true"></i> 一键随机概率
                </button>
                
                <!-- 历史运行结果按钮 -->
                <button type="button" class="btn btn-sm btn-info" id="historyBtn">
                    <i class="fa fa-history" aria-hidden="true"></i> 历史运行结果
                </button>
            </div>
        </div>

        <!-- 解析结果区域 -->
        <div id="analysisContent">
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">请耐心等待约十秒钟，正在解析问卷内容...</div>
            </div>
        </div>

        <!-- 刷问卷按钮 -->
        <button type="button" class="btn btn-success" id="brushBtn" style="margin-top: 20px; display: none;">
            <i class="fa fa-play" aria-hidden="true"></i> 准备就绪！开刷
        </button>
    </div>
</div>

<!-- 文本答案配置弹窗 -->
<div id="textAnswerModal" class="modal">
    <div class="modal-content">
        <div style="position: relative; margin-bottom: 15px;">
            <h5 style="margin: 0; padding-right: 30px;">配置该题文本答案(总概率相加须得100)</h5>
            <span class="close" style="position: absolute; top: 0; right: 0;">&times;</span>
        </div>
        <div id="answerList">
            <div class="answer-item" style="display: flex; align-items: center; margin-bottom: 10px;">
                <label for="answerText0"></label><input type="text" id="answerText0" class="answer-text form-control" placeholder="输入文本答案" style="flex: 2; margin-right: 10px;">
                <div style="display: flex; align-items: center;">
                    <label for="answerProb0"></label><input type="number" id="answerProb0" class="probability-input form-control" placeholder="概率" min="0" max="100" style="width: 80px; margin-right: 5px;">
                    <span style="margin-right: 10px;">%</span>
                </div>
                <button type="button" class="btn btn-sm btn-danger" onclick="removeAnswerItem(this)" style="min-width: 60px;">删除</button>
            </div>
        </div>
        <div style="margin-bottom: 15px;">
            <button type="button" class="btn btn-sm btn-primary" onclick="addAnswerItem()" style="min-width: 80px;">添加答案</button>
        </div>
        <button type="button" class="btn btn-primary" onclick="saveTextAnswers()" style="min-width: 80px;">保存</button>
    </div>
</div>

<script>
// 为初始输入框添加blur事件监听器
function addBlurListenersToInitialInputs() {
    const answerList = document.getElementById('answerList');
    if (answerList) {
        const answerItems = answerList.getElementsByClassName('answer-item');
        for (let i = 0; i < answerItems.length; i++) {
            const item = answerItems[i];
            const textInput = item.getElementsByClassName('answer-text')[0];
            const probabilityInput = item.getElementsByClassName('probability-input')[0];
            
            if (textInput && probabilityInput) {
                textInput.addEventListener('blur', function() {
                    validateSingleAnswerItem(textInput, probabilityInput);
                });
                
                probabilityInput.addEventListener('blur', function() {
                    validateSingleAnswerItem(textInput, probabilityInput);
                });
            }
        }
    }
}

// 页面加载完成后为初始输入框添加监听器
window.addEventListener('DOMContentLoaded', function() {
    addBlurListenersToInitialInputs();
});
</script>

<!-- 系统使用简介弹窗 -->
<div id="usageIntroModal" class="modal">
    <div class="modal-content" style="width: 800px; max-height: 80vh; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); margin: 0; z-index: 1001;">
        <div style="position: relative; margin-bottom: 15px;">
            <h5 style="margin: 0; padding-right: 30px;">系统使用须知</h5>
            <span class="close" style="position: absolute; top: 0; right: 0;">&times;</span>
        </div>
        <div style="margin-top: 20px; max-height: 60vh; overflow-y: auto;">
            <p>系统目前支持单选题，多选题，填空题，量表题，矩阵题，理论上支持排序题</p>
            <br>
            
            <h6 style="font-weight: bold; color: #333;">单选题</h6>
            <div style="text-align: center; margin: 15px 0;">
                <img src="static/pictures/单选.png" alt="单选题示例" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <p>每道题需要设置n份问卷每个选项出现的概率，每道题各个选项概率和应为100，如果选项需要填入文本，则需要点击编辑文本答案</p>
            <div style="text-align: center; margin: 15px 0;">
                <img src="static/pictures/编辑文本答案.png" alt="编辑文本答案示例" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <p>然后需要你手动输入这道题的回答，每一个答案占一行，需要新增答案则点击添加答案，所有答案概率和应为100</p>
            <br>
            
            <h6 style="font-weight: bold; color: #333;">多选题</h6>
            <div style="text-align: center; margin: 15px 0;">
                <img src="static/pictures/多选.png" alt="多选题示例" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <p>多选题同单选题</p>
            <br>
            
            <h6 style="font-weight: bold; color: #333;">填空题</h6>
            <div style="text-align: center; margin: 15px 0;">
                <img src="static/pictures/填空.png" alt="填空题示例" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <p>填空题类似于单选题的点击编辑文本答案</p>
            <br>
            
            <h6 style="font-weight: bold; color: #333;">量表题</h6>
            <div style="text-align: center; margin: 15px 0;">
                <img src="static/pictures/量表.png" alt="量表题示例" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <p>量表题则是所有选择概率和为100，注意不要漏填，也许后面还没没展示的选项</p>
            <br>
            
            <h6 style="font-weight: bold; color: #333;">矩阵题</h6>
            <div style="text-align: center; margin: 15px 0;">
                <img src="static/pictures/矩阵.png" alt="矩阵题示例" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <p>矩阵题每一行算一个题，一行的概率和为100，如我图中画出的红框</p>
            <br>
            
            <p>问卷总份数在<span style="color: red; font-weight: bold;">10~200份</span>之间，可以利用 <span style="color: red; font-weight: bold;">一键随机概率按钮</span> 来快速设置概率，两百份问卷大约耗时半个小时</p>
        </div>
        <button type="button" class="btn btn-primary" style="margin-top: 20px; min-width: 80px;" onclick="document.getElementById('usageIntroModal').style.display = 'none'">关闭</button>
    </div>
</div>

<!-- 历史运行结果弹窗 -->
<div id="historyModal" class="modal">
    <div class="modal-content" style="width: 500px; max-height: 600px; overflow-y: auto;">
        <div style="position: relative; margin-bottom: 15px;">
            <h5 style="margin: 0; padding-right: 30px;">历史运行结果</h5>
            <span class="close" style="position: absolute; top: 0; right: 0;">&times;</span>
        </div>
        <div id="historyContent" style="margin-top: 20px;">
            <div style="text-align: center; color: #666; padding: 20px;">暂无历史运行记录</div>
        </div>
        <button type="button" class="btn btn-primary" style="margin-top: 20px; min-width: 80px;" onclick="document.getElementById('historyModal').style.display = 'none'">关闭</button>
    </div>
</div>

<!-- 引入请求工具 -->
<script src="${pageContext.request.contextPath}/static/js/request.js"></script>
<!-- 引入API封装 -->
<script src="${pageContext.request.contextPath}/static/js/api.js"></script>
<!-- 引入Bootstrap JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<!-- 引入自定义JS -->
<script src="${pageContext.request.contextPath}/static/js/alert.js"></script>
<!-- 引入概率检测工具 -->
<script src="${pageContext.request.contextPath}/static/js/probability-validator.js"></script>
<!-- 引入分析页面主逻辑 -->
<script src="${pageContext.request.contextPath}/static/js/analysis.js"></script>

<script>
    // 确认返回首页的函数
    function confirmBack() {
        if (confirm('返回首页后当前页面将会清空，是否返回？')) {
            history.back();
        }
    }
</script>
</body>
</html>