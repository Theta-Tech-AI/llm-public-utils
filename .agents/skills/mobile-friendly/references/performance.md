# ⚡ Measure mobile performance

Add this check when the page loads slowly, a tap takes too long, the content moves while the user reads it, or the fix changes what the page loads or renders. Keep the screenshot loop for layout and hierarchy.

## 🔁 Record, change, and record again

1. 📍 Pick one route, viewport, fixture, and action. Use the first useful content for a load test, and a real task such as opening a filter, typing in an editor, or choosing a row for an interaction test.
2. 🎛️ Test a production build on localhost. Use the hot-reload preview for screenshots. In Chrome DevTools Performance, record the device or viewport, CPU and network throttling, and cache state. Use matching settings before and after. Run a cold load and a warm repeat if cache behavior matters.
3. 📏 Record the baseline. Save a load trace for Largest Contentful Paint (LCP) and Cumulative Layout Shift (CLS), and an interaction trace for the selected tap or keypress. Record transferred bytes or request timing when relevant. Repeat under the same conditions when measurements vary. [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/overview)
4. 🛠️ Find the request, long task, or layout shift that explains the problem. Change one cause, repeat the interaction, and compare traces and fresh screenshots. Confirm the action still works and visible feedback appears when the user needs it.
5. ☁️ Check the affected page on the deployed build. Record local and deployed results separately. Device emulation approximates a phone. Use a real phone for claims about browser chrome, keyboard behavior, or device performance. [Chrome DevTools device mode](https://developer.chrome.com/docs/devtools/device-mode)

## 🔍 Where to look

- 🖼️ **Slow first useful content.** Look for oversized images, late fonts, blocking requests, and work that can start after the first screen. Size images to their display width and prioritize media that is the LCP element. Use the trace to check when the element starts loading and renders. [Optimize LCP](https://web.dev/articles/optimize-lcp)
- 👆 **Slow taps or typing.** Look for long main-thread tasks, synchronous rendering of large lists or charts, and scripts that start when the page opens. Check input delay, handler time, and presentation delay. [Optimize INP](https://web.dev/articles/optimize-inp)
- 🧭 **Uneven scrolling.** Record a scroll in the Performance panel. Check dropped frames, long rendering tasks, and paint-heavy content during the scroll. [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/overview)
- 📐 **Content jumps.** Inspect layout shift events. Check image and chart dimensions, skeleton sizes, late banners, and font swaps. Reserve room for media and delayed content. [Optimize CLS](https://web.dev/articles/optimize-cls)
- 📡 **Slow data or repeat work.** Use the network waterfall to find duplicate requests and dependencies that run in series. Compare with server timings when available. Keep screen data and cache state consistent across runs.

## 📊 Report the result

Record route and build, viewport and device, fixture and action, throttle settings and cache state, before and after values, and paths to traces and screenshots. Label a measured tap as a lab interaction. Use field data to report Core Web Vitals for real users. The good field thresholds at the 75th percentile of mobile visits are LCP ≤ 2.5 s, Interaction to Next Paint (INP) ≤ 200 ms, and CLS ≤ 0.1. [Web Vitals](https://web.dev/articles/vitals)
