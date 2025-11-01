// ==UserScript==
// @name         QQ Docs Auto Fill
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  自动填腾讯文档表单
// @author       Ranxy
// @match        https://docs.qq.com/form/page/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // ✅ 1. 定义填报内容数组
    const inputList = [
        '名字',
        '学号',
        '学院',
        '...',
        '...'
    ];

    // ✅ 2. 页面加载完成后执行主逻辑
    window.addEventListener('load', () => {
        console.log('页面加载完成');

        // ✅ 3. 查找所有输入框
        let elements = document.querySelectorAll("textarea[placeholder='请输入']");
        if (elements.length === 0) {
            console.error('没有找到输入框');
            return;
        }

        // ✅ 4. 遍历输入框，填入数据
        for (let i = 0; i < Math.min(inputList.length, elements.length); i++) {
            elements[i].value = inputList[i];
            // 🔑 触发 input 事件，让页面识别输入
            elements[i].dispatchEvent(new Event('input', { bubbles: true }));
        }

        // ✅ 5. 点击提交按钮
        let submitButton = Array.from(document.querySelectorAll('button'))
                                .find(b => b.textContent.includes('提交'));
        if (submitButton) {
            submitButton.click();
            console.log('已提交');
        } else {
            console.error('未找到提交按钮');
        }

        // ✅ 6. 点击确认按钮（延迟执行）
        setTimeout(() => {
            let confirmButton = Array.from(document.querySelectorAll('button'))
                                     .find(b => b.textContent.includes('确认'));
            if (confirmButton) confirmButton.click();
            console.log('完成确认');
        }, 500); // 延迟0.5秒
    });
})();
