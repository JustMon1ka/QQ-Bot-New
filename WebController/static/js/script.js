let isLoggingActive = true;
let isCleared = false; // 标记是否点击过清除按钮
let lastSize = 0;
let logUpdateTimer = null;

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
    if (!isCleared) {
        loadLogContent();
    }

    const logOutputDiv = document.getElementById('log-output');
    if (logOutputDiv) {
        loadLogContent();
    }

    const clearLogButton = document.getElementById('clear-log');
    if (clearLogButton) {
        clearLogButton.addEventListener('click', function() {
            fetch('/clear-log', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('log-output').innerHTML = '';
                        lastSize = 0;  // 确保清除后重置已读取的日志大小
                    }
                })
        });
    }

    const toggleLogButton = document.getElementById('toggle-log');
    if (toggleLogButton) {
        toggleLogButton.addEventListener('click', function() {
            Element
            let iconSpan = null;
            if(isLoggingActive){
                iconSpan = this.querySelector('span.pause-icon');
            }
            else {
                iconSpan = this.querySelector('span.play-icon');
            }
            isLoggingActive = !isLoggingActive;
            iconSpan.classList.toggle('play-icon');
            iconSpan.classList.toggle('pause-icon');
            if (isLoggingActive) {
                loadLogContent();
            }
        });
    }
}

async function loadLogContent() {
    if (!isLoggingActive) {
        clearTimeout(logUpdateTimer);
        return;
    }

    const response = await fetch('/log.out');
    const text = await response.text();
    const logOutputDiv = document.getElementById('log-output');
    logOutputDiv.innerHTML += formatLog(text.replace(/\n/g, '<br>')); // 添加新内容

    clearTimeout(logUpdateTimer); // 清除之前的定时器
    logUpdateTimer = setTimeout(loadLogContent, 5000); // 设置新的定时器
}

function formatLog(text) {
    return text
        .replace(/\[ERROR\](.*?)<br>/g, '<span style="color: red;">[ERROR]$1</span><br>')
        .replace(/\[WARNING\](.*?)<br>/g, '<span style="color: orange;">[WARNING]$1</span><br>')
        .replace(/\[INFO\](.*?)<br>/g, '<span style="color: green;">[INFO]$1</span><br>')
        .replace(/\[DEBUG\](.*?)<br>/g, '<span style="color: blue;">[DEBUG]$1</span><br>');
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
    console.log(currentStatus);  // Log the current status
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