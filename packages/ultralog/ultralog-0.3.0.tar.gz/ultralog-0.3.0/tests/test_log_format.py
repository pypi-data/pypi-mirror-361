import unittest
from ultralog import UltraLog
import io
import sys


class TestLogFormat(unittest.TestCase):
    def setUp(self):
        self.stderr = io.StringIO()
        sys.stderr = self.stderr

    def tearDown(self):
        sys.stderr = sys.__stderr__

    def test_default_format(self):
        """测试默认日志格式"""
        logger = UltraLog(console_output=True)
        logger.info("test message")
        
        # 获取控制台输出
        output = self.stderr.getvalue().strip()
        
        # 验证日志输出格式
        # 验证日志格式的关键组成部分
        self.assertIn("| INFO     | UltraLog |", output)
        self.assertIn(" - test message", output)
        self.assertRegex(output, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+")

    def test_custom_name_format(self):
        """测试自定义名称的日志格式"""
        logger = UltraLog(name="CustomLogger", console_output=True)
        logger.info("test message")
        
        # 获取控制台输出
        output = self.stderr.getvalue().strip()
        
        # 验证日志输出格式
        # 验证日志格式的关键组成部分
        self.assertIn("| INFO     | CustomLogger |", output)
        self.assertIn(" - test message", output)
        self.assertRegex(output, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+")

    def test_log_levels(self):
        """测试不同日志级别的格式"""
        logger = UltraLog(console_output=True)
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in levels:
            with self.subTest(level=level):
                self.stderr = io.StringIO()
                sys.stderr = self.stderr
                
                getattr(logger, level.lower())("test message")
                
                output = self.stderr.getvalue().strip()
                # 验证日志级别显示正确
                self.assertIn(f"| {level.ljust(8)} |", output)

if __name__ == "__main__":
    unittest.main()
