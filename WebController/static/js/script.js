let logCache = ''; // 存储所有日志
let errorCount = 0; // 错误日志计数
let isDisplayActive = true; // 控制是否将日志显示到输出栏
let nowSection = ''; // 记录当成处在的选项页的ID

async function loadHtmlContent(sectionId, url, callback=null) {
    // 从服务器获取HTML内容
    const response = await fetch(url);
    const htmlContent = await response.text();

    // 隐藏所有内容区域
    document.querySelectorAll('.content-section').forEach(function(section) {
        section.classList.add('hidden');
    });

    // 显示选中的内容区域并设置其HTML内容
    const section = document.getElementById(sectionId);
    section.innerHTML = htmlContent;
    section.classList.remove('hidden');

    // 更新导航栏的活动状态
    updateActiveNav(sectionId);
    if (nowSection === 'logOutput' && nowSection !== sectionId){
        await fetch("./leave-log.html")
    }
    nowSection = sectionId

    // 如果是加载日志输出，初始化日志查看器
    if (sectionId === 'logOutput') {
        initializeLogViewer();
    }
    // 如果是显示基础信息，初始化基础信息元素
    if (sectionId === 'baseInfo') {
        setupCollapsible();
    }
    if (callback){
        callback();
    }
}

function updateActiveNav(activeSectionId) {
    document.querySelectorAll('.nav-item').forEach(function(item) {
        if (item.getAttribute('onclick').includes(activeSectionId)) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

document.addEventListener("DOMContentLoaded", function() {
    var coll = document.getElementsByClassName("collapsible-button");
    for (var i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            var contentPanels = document.querySelectorAll('.collapsible-content');
            contentPanels.forEach(panel => {
                if (panel !== this.nextElementSibling) {
                    panel.style.display = 'none';
                }
            });

            var content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
    loadLogContent();  // 启动日志加载功能
});

function setupCollapsible() {
    document.querySelectorAll('.collapsible-button').forEach(button => {
        button.addEventListener('click', function() {
            var content = this.nextElementSibling;
            if (content.style.maxHeight && content.style.maxHeight !== "0px") {
                content.style.maxHeight = "0px";
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
            }
        });
    });
}

function navigateToPlugin(pluginName) {
    loadHtmlContent('pluginsManagement', './plugins.html', function() {
        const pluginElement = document.getElementById(pluginName);
        if (pluginElement) {
            pluginElement.scrollIntoView({ behavior: 'smooth' }); // 滚动到插件
            const detailsButton = pluginElement.querySelector('.collapsible');
            detailsButton.click(); // 触发点击以展开详细信息
        }
    });
}

// 初始展示“基础信息”
document.addEventListener("DOMContentLoaded", function() {
    // 如果初始页面加载就包含折叠组件
    setupCollapsible();
    loadHtmlContent('baseInfo', './baseInfo.html'); // 初始加载基础信息
});


// 以下是用于log.html的js
function initializeLogViewer() {
    const logOutputDiv = document.getElementById('log-output');
    const clearLogButton = document.getElementById('clear-log');
    const toggleLogButton = document.getElementById('toggle-log');

    // 监听清除日志按钮事件
    if (clearLogButton) {
        clearLogButton.addEventListener('click', function() {
            fetch('/clear-log', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        logOutputDiv.innerHTML = ''; // 清空日志显示
                        logCache = ''; // 也清空日志缓存
                        errorCount = 0; // 重置错误计数
                    }
                });
        });
    }

    // 控制日志的持续加载和暂停
    if (toggleLogButton) {
        toggleLogButton.addEventListener('click', function() {
            isDisplayActive = !isDisplayActive; // 切换显示状态
            const iconSpan = this.querySelector(isDisplayActive ? 'span.play-icon' : 'span.pause-icon');
            iconSpan.classList.toggle('play-icon');
            iconSpan.classList.toggle('pause-icon');

            // 如果重新激活显示并有缓存数据，立即显示
            if (isDisplayActive && logCache) {
                const logOutputDiv = document.getElementById('log-output');
                logOutputDiv.innerHTML += logCache.replace(/\n/g, '<br>');
                logCache = ''; // 清空缓存
            }
        });
    }

    const logViewer = document.querySelector('.log-viewer');
    const scrollToBottomBtn = document.querySelector('.scroll-to-bottom');

    logViewer.addEventListener('scroll', function() {
        const isAtBottom = logViewer.scrollHeight - logViewer.clientHeight <= logViewer.scrollTop + 1;
        // console.log(isAtBottom)
        scrollToBottomBtn.style.display = isAtBottom ? 'none' : 'block';
        // console.log(scrollToBottomBtn.style.display)
    });

    scrollToBottomBtn.addEventListener('click', function() {
        logViewer.scrollTop = logViewer.scrollHeight;
        scrollToBottomBtn.style.display = 'none';
    });

    // 初始调用更新滚动视图
    updateLogViewer(logViewer, scrollToBottomBtn);
}

function updateLogViewer(logViewer, scrollToBottomBtn) {
    // 检查是否处于底部，如果不是，则显示按钮
    if (logViewer.scrollTop + logViewer.clientHeight < logViewer.scrollHeight) {
        scrollToBottomBtn.style.display = 'block';
    } else {
        scrollToBottomBtn.style.display = 'none';
    }
}

async function loadLogContent() {
    while (true) { // 创建一个无限循环，始终运行直至页面关闭
        const response = await fetch('/log.out');
        const newText = await response.text();
        logCache += newText; // 追加新日志到缓存
        const scrollToBottomBtn = document.querySelector('.scroll-to-bottom');

        // 检查新日志中是否含有错误
        const newErrors = (newText.match(/\[ERROR\]/g) || []).length;
        errorCount += newErrors;

        if (newErrors > 0) {
            updateLogAlert(errorCount); // 更新错误提示
        }

        if (nowSection === "logOutput") { // 只有当前选项页是“日志输出”时，才考虑将日志写入
            if (isDisplayActive) { // 当显示激活时，更新日志输出栏
                const logOutputDiv = document.getElementById('log-output');
                logOutputDiv.innerHTML += formatLog(logCache.replace(/\n/g, '<br>')); // 添加新内容
                logCache = ''; // 清空缓存
                clearLogAlert()
            }
        }

        await new Promise(resolve => setTimeout(resolve, 1000)); // 每1秒执行一次
    }
}

function updateLogAlert(count) {
    const logTab = document.getElementById('nav-logOutput');
    const errorIndicator = document.getElementById('error-count');

    if (count > 0) {
        logTab.classList.add('highlight'); // 添加高亮类
        errorIndicator.innerHTML = `<span class="error-circle">${count}</span>`; // 显示错误计数
    } else {
        clearLogAlert(); // 如果没有错误，清除高亮
    }
}

function clearLogAlert() {
    const logTab = document.getElementById('nav-logOutput');
    const errorIndicator = document.getElementById('error-count');
    logTab.classList.remove('highlight'); // 移除高亮类
    errorIndicator.innerHTML = ''; // 清空错误计数显示
    errorCount = 0;
}

// document.querySelectorAll('.nav-item').forEach(item => {
//     item.addEventListener('click', function() {
//         const sectionId = this.getAttribute('data-section');
//         if (sectionId === 'logOutput') {
//             document.getElementById('log-output').innerHTML = formatLog(logCache.replace(/\n/g, '<br>'));
//             errorCount = 0; // 重置错误计数
//             clearLogAlert(); // 清除错误提示
//         }
//     });
// });

function formatLog(text) {
    return text
        .replace(/\[ERROR\](.*?)<br>/g, '<span style="color: red;">[ERROR]$1</span><br>')
        .replace(/\[error\](.*?)<br>/g, '<span style="color: #8d8d8d;">[ERROR]$1</span><br>')
        .replace(/\[WARNING\](.*?)<br>/g, '<span style="color: orange;">[WARNING]$1</span><br>')
        .replace(/\[INFO\](.*?)<br>/g, '<span style="color: green;">[INFO]$1</span><br>')
        .replace(/\[DEBUG\](.*?)<br>/g, '<span style="color: #5959ff;">[DEBUG]$1</span><br>');
}

// plugins.html中使用的js
function togglePluginDetails(pluginId) {
    var details = document.getElementById(pluginId).querySelector('.plugin-details');
    if (details.classList.contains('open')) {
        details.classList.remove('open');
        details.style.maxHeight = null; // Collapse the section
    } else {
        // Close all other open details
        var allDetails = document.querySelectorAll('.plugin-details.open');
        allDetails.forEach(function(detail) {
            detail.classList.remove('open');
            detail.style.maxHeight = null;
        });

        // Open this detail
        details.classList.add('open');
        details.style.maxHeight = details.scrollHeight + "px"; // Set max-height to the scrollHeight to expand
    }
}

function searchPlugins() {
    let input = document.getElementById('plugin-search');
    let filter = input.value.toUpperCase();
    let pluginsContainer = document.getElementById('plugins-container');
    let plugins = pluginsContainer.getElementsByClassName('plugin-item');
    for (let i = 0; i < plugins.length; i++) {
        let title = plugins[i].getElementsByClassName('plugin-title')[0];
        if (title.innerText.toUpperCase().indexOf(filter) > -1) {
            plugins[i].style.display = "";
        } else {
            plugins[i].style.display = "none";
        }
    }
}

function togglePluginStatus(pluginName, currentStatus) {
    const newStatus = currentStatus === 'running' ? 'disable' : 'running';
    const statusElementId = `status-${pluginName.toLowerCase()}`;
    fetch(`/toggle-plugin-status/${pluginName}/${newStatus}`, {
        method: 'POST'
    }).then(response => response.json())
        .then(data => {
            if (data.success) {
                const button = document.querySelector(`#button-${pluginName}`);
                if (button) {
                    button.setAttribute('data-status', newStatus);  // Update the data-status attribute
                    button.onclick = function() { togglePluginStatus(pluginName, newStatus); }; // Update onclick to the new status
                    if (newStatus === 'disable') {
                        button.classList.add('button-disable');
                        button.textContent = '启用';
                    } else {
                        button.classList.remove('button-disable');
                        button.textContent = '禁用';
                    }
                }
                const statusElement = document.getElementById(statusElementId);
                if (statusElement) {
                    statusElement.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1); // First letter capitalize
                    statusElement.className = `plugin-status status-${newStatus.toLowerCase()}`; // Update class for new status
                }
            } else {
                alert('状态更新失败: ' + data.message);
            }
        }).catch(error => {
        console.error('Error updating plugin status:', error);
    });
}

function removeRow(button) {
    const row = button.closest('tr');
    row.remove();
}

function addRow(button) {
    const table = button.previousElementSibling;
    const tbody = table.querySelector('.table-body');
    const newRow = tbody.insertRow();
    const newCell = newRow.insertCell(0);

    const input = document.createElement('input');
    input.type = 'text';
    input.classList.add('textbox');
    newCell.appendChild(input);

    const removeButtonCell = newRow.insertCell(1);
    const removeButton = document.createElement('button');
    removeButton.textContent = '删除';
    removeButton.classList.add('remove-button');
    removeButton.setAttribute('onclick', 'removeRow(this)');
    removeButtonCell.appendChild(removeButton);
}

function toggleEditConfig(container, button) {
    const isEditing = button.textContent === '保存配置';
    const inputs = container.querySelectorAll('input, .add-button, .remove-button');

    inputs.forEach(input => {
        if (isEditing) {
            input.setAttribute('disabled', true);

            // 如果是文本框，保存其值并替换为文本
            if (input.tagName === 'INPUT' && input.type === 'text') {
                const td = input.closest('td');
                if (td && !td.querySelector('span')) {
                    const span = document.createElement('span');
                    span.textContent = input.value;
                    td.appendChild(span);
                    input.remove();
                }
            }
        } else {
            input.removeAttribute('disabled');

            // 如果是 span，将其替换回文本框
            const span = input.closest('td') ? input.closest('td').querySelector('span') : null;
            if (span) {
                const newInput = document.createElement('input');
                newInput.type = 'text';
                newInput.value = span.textContent;
                newInput.classList.add('textbox');
                newInput.removeAttribute('disabled');
                span.parentNode.appendChild(newInput);
                span.remove();
            }
        }
    });

    if (isEditing) {
        const configData = collectConfigData(container);
        saveConfigData(configData);
        loadHtmlContent("pluginsManagement", "./plugins.html")
    }

    button.textContent = isEditing ? '修改配置' : '保存配置';
    button.style.backgroundColor = isEditing ? '#007bff' : '#ff0000'; // 切换按钮颜色
    button.style.color = isEditing ? 'white' : 'white'; // 确保文本颜色正确
}

function collectConfigData(container) {
    const configData = {};
    const items = container.querySelectorAll('.config-item');

    items.forEach(item => {
        const label = item.querySelector('label');
        if (label) {
            const key = label.textContent.trim();
            const input = item.querySelector('input');
            if (input) {
                if (input.type === 'checkbox') {
                    configData[key] = input.checked;
                } else {
                    configData[key] = input.value;
                }
            }
        }

        const table = item.querySelector('table');
        if (table) {
            const key = table.querySelector('th').textContent.trim();
            const values = [];
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const cell = row.querySelector('td:first-child');
                if (cell) {
                    values.push(cell.textContent.trim());
                }
            });
            configData[key] = values;
        }
    });

    configData["plugin_name"] = container.closest('.plugin-item').id;
    return configData;
}

function saveConfigData(configData) {
    fetch('/save_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(configData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('配置保存成功');
            } else {
                alert('配置保存失败: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('配置保存失败: ' + error.message);
        });
}