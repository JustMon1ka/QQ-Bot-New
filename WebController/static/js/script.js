async function loadHtmlContent(sectionId, url) {
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
}

function changeContent(sectionId) {
    // 隐藏所有内容区域
    document.querySelectorAll('.content-section').forEach(function(section) {
        section.classList.add('hidden');
    });

    // 显示选中的内容区域
    document.getElementById(sectionId).classList.remove('hidden');

    // 更新导航栏的活动状态
    updateActiveNav(sectionId);
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

// 初始展示“基础信息”
document.addEventListener('DOMContentLoaded', function() {
    changeContent('baseInfo');
});