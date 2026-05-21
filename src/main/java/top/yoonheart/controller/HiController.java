package top.yoonheart.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

//欢迎界面
@Controller
public class HiController {

    @GetMapping("/")
    public String home(Model model) {
        return "index";
    }

    @GetMapping("/analysis")
    public String analysis() {
        return "analysis";
    }
}