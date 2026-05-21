// 不阻塞提示函数
function showAlert(message, type = 'error') {
    // 创建提示框元素
    const alertDiv = document.createElement('div');
    alertDiv.className = `custom-alert custom-alert-${type}`;
    alertDiv.innerHTML = message;
    
    // 设置样式
    Object.assign(alertDiv.style, {
        position: 'fixed',
        top: '20px',
        left: '50%',
        transform: 'translate(-50%, 0) scale(0.8)',
        padding: '12px 24px',
        borderRadius: '8px',
        color: 'white',
        fontSize: '14px',
        fontWeight: '600',
        zIndex: '9999',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)',
        opacity: '0',
        transition: 'all 0.3s ease'
    });
    
    // 根据类型设置背景色
    if (type === 'error') {
        alertDiv.style.backgroundColor = '#f44336';
    } else if (type === 'success') {
        alertDiv.style.backgroundColor = '#4caf50';
    } else if (type === 'info') {
        alertDiv.style.backgroundColor = '#2196f3';
    }
    
    // 添加到页面
    document.body.appendChild(alertDiv);
    
    // 显示动画
    setTimeout(() => {
        alertDiv.style.opacity = '1';
        alertDiv.style.transform = 'translate(-50%, 0) scale(1)';
    }, 100);
    
    // 3秒后自动隐藏
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        alertDiv.style.transform = 'translate(-50%, 0) scale(0.8)';
        
        // 动画结束后移除元素
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 300);
    }, 3000);
}

// 导出函数（如果需要模块使用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { showAlert };
}