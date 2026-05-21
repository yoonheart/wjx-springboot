// RESTful风格请求工具

// 基础配置
const baseUrl = '';

// 通用请求函数
function request(url, method = 'GET', data = null, headers = {}) {
    return new Promise((resolve, reject) => {
        let fullUrl = baseUrl + url;
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                ...headers
            },
            credentials: 'include'
        };
        
        // 根据请求方法处理数据
        if (data) {
            if (method === 'GET' || method === 'DELETE') {
                // GET/DELETE请求将数据转换为查询参数
                const queryParams = new URLSearchParams(data).toString();
                fullUrl = queryParams ? `${fullUrl}?${queryParams}` : fullUrl;
            } else {
                // POST/PUT/PATCH请求处理
                if (typeof data === 'string') {
                    // 如果是字符串，直接使用
                    options.body = data;
                } else {
                    // 否则转换为JSON
                    options.body = JSON.stringify(data);
                }
            }
        }
        
        // 发送请求
        fetch(fullUrl, options)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // 检查后端返回的业务错误码
                if (data.code !== undefined && data.code !== 1) {
                    throw new Error(data.msg || '请求失败');
                }
                resolve(data);
            })
            .catch(error => reject(error));
    });
}

// 封装常用请求方法
const requestUtil = {
    // GET请求
    get(url, data = null, headers = {}) {
        return request(url, 'GET', data, headers);
    },
    
    // POST请求
    post(url, data = null, headers = {}) {
        return request(url, 'POST', data, headers);
    },
    
    // PUT请求
    put(url, data = null, headers = {}) {
        return request(url, 'PUT', data, headers);
    },
    
    // DELETE请求
    delete(url, data = null, headers = {}) {
        return request(url, 'DELETE', data, headers);
    },
    
    // PATCH请求
    patch(url, data = null, headers = {}) {
        return request(url, 'PATCH', data, headers);
    }
};

// 将请求工具挂载到window对象上，以便普通脚本访问
window.requestUtil = requestUtil;