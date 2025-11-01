// ==UserScript==
// @name         QQ Docs Auto Fill with Timer
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  自动填腾讯文档表单，支持定时执行
// @author       RanxyCoder
// @match        https://docs.qq.com/form/page/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // 1️⃣ 定义填报内容
    const inputList = [
        '名字',
        '学号',
        '学院',
        '...',
        '...'
    ];

    // 2️⃣ 定义目标执行时间 (年, 月-1, 日, 时, 分, 秒)
    // 注意：月份是从0开始，0=1月，10=11月
    const targetTime = new Date(2025, 10, 1, 19, 0, 0);

    // 3️⃣ 主逻辑函数：执行填表
    function fillForm() {
        console.log('开始填表，时间：', new Date());

        // 找到所有输入框
        let elements = document.querySelectorAll("textarea[placeholder='请输入']");
        if (elements.length === 0) {
            console.error('没有找到输入框');
            return;
        }

        // 填入数据
        for (let i = 0; i < Math.min(inputList.length, elements.length); i++) {
            elements[i].value = inputList[i];
            elements[i].dispatchEvent(new Event('input', { bubbles: true }));
        }

        // 点击提交按钮
        let submitButton = Array.from(document.querySelectorAll('button'))
                                .find(b => b.textContent.includes('提交'));
        if (submitButton) submitButton.click();
        else console.error('未找到提交按钮');

        // 点击确认按钮，延迟 0.5 秒
        setTimeout(() => {
            let confirmButton = Array.from(document.querySelectorAll('button'))
                                     .find(b => b.textContent.includes('确认'));
            if (confirmButton) confirmButton.click();
            console.log('填表完成');
        }, 500);
    }

    // 4️⃣ 定时器：等待到指定时间再执行
    function waitUntil(targetDate, callback) {
        const now = new Date();
        const delay = targetDate - now;

        if (delay <= 0) {
            console.log('目标时间已过，立即执行');
            callback();
        } else {
            console.log(`等待开始... 目标时间：${targetDate.toLocaleString()}, 还有 ${(delay/1000).toFixed(1)} 秒`);
            setTimeout(callback, delay);
        }
    }

    // 5️⃣ 页面加载完成后启动定时器
    window.addEventListener('load', () => {
        console.log('页面加载完成');
        waitUntil(targetTime, fillForm);
    });

})();
