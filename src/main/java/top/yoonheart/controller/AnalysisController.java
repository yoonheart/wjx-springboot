package top.yoonheart.controller;

import org.springframework.web.bind.annotation.*;
import top.yoonheart.config.PythonExecutor;
import top.yoonheart.po.Result;

import java.io.UnsupportedEncodingException;
import java.net.URL;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

@RestController
@RequestMapping("/api/analysis")
public class AnalysisController {

    @GetMapping
    public Result analysis(String url) throws UnsupportedEncodingException {
        // 1. 先校验前端传的url参数非空
        if (url == null || url.trim().isEmpty()) {
            return Result.error("问卷网址不能为空，请检查参数");
        }

            // 2. 获取resources/scripts/scan.py的资源URL（核心：路径要和实际文件一致）
            URL resourceUrl = getClass().getClassLoader().getResource("scripts/scan.py");

            // 3. 空指针防护：如果找不到脚本，直接返回错误
            if (resourceUrl == null) {
                return Result.error("未找到Python脚本，请检查文件路径：src/main/resources/scripts/scan.py");
            }

            // 4. 解码路径（解决中文/空格/特殊字符导致的路径错误）
            String scriptPath = URLDecoder.decode(resourceUrl.getPath(), StandardCharsets.UTF_8);

            // 5. 处理Windows系统路径格式
            if (System.getProperty("os.name").toLowerCase().contains("win")) {
                // 移除开头的斜杠
                if (scriptPath.startsWith("/")) {
                    scriptPath = scriptPath.substring(1);
                }
                // 将正斜杠转换为反斜杠
                scriptPath = scriptPath.replace("/", "\\");
            }

            // 5. 执行Python脚本（增加异常捕获，避免脚本执行失败导致接口崩溃）
            String result = PythonExecutor.executePythonScript(scriptPath, url);

            // 6. 返回执行结果
            return Result.success(result);

    }
}