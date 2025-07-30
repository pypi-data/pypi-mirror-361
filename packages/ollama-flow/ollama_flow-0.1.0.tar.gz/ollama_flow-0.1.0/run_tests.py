#!/usr/bin/env python3
"""
測試運行腳本
提供各種測試運行選項
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """運行命令並顯示結果"""
    print(f"\n{'='*60}")
    if description:
        print(f"正在執行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Ollama Flow 測試運行器")
    parser.add_argument("--unit", action="store_true", help="只運行單元測試")
    parser.add_argument("--integration", action="store_true", help="只運行整合測試")
    parser.add_argument("--coverage", action="store_true", help="生成覆蓋率報告")
    parser.add_argument("--html", action="store_true", help="生成 HTML 覆蓋率報告")
    parser.add_argument("--slow", action="store_true", help="包含慢速測試")
    parser.add_argument("--parallel", action="store_true", help="並行運行測試")
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細輸出")
    parser.add_argument("--file", "-f", help="運行特定測試文件")
    parser.add_argument("--function", "-k", help="運行特定測試函數")
    parser.add_argument("--install-deps", action="store_true", help="安裝測試依賴")
    
    args = parser.parse_args()
    
    # 檢查是否在項目根目錄
    if not Path("ollama_flow").exists():
        print("錯誤: 請在項目根目錄運行此腳本")
        sys.exit(1)
    
    # 安裝測試依賴
    if args.install_deps:
        print("正在安裝測試依賴...")
        deps_cmd = [
            sys.executable, "-m", "pip", "install", 
            "pytest", "pytest-cov", "pytest-xdist", "pytest-mock"
        ]
        if not run_command(deps_cmd, "安裝測試依賴"):
            print("依賴安裝失敗")
            sys.exit(1)
    
    # 構建pytest命令
    pytest_cmd = [sys.executable, "-m", "pytest"]
    
    # 添加詳細輸出
    if args.verbose:
        pytest_cmd.append("-v")
    
    # 添加覆蓋率選項
    if args.coverage or args.html:
        pytest_cmd.extend(["--cov=ollama_flow", "--cov-report=term-missing"])
        if args.html:
            pytest_cmd.append("--cov-report=html")
    
    # 添加並行執行
    if args.parallel:
        pytest_cmd.extend(["-n", "auto"])
    
    # 添加標記過濾
    if args.unit:
        pytest_cmd.extend(["-m", "unit"])
    elif args.integration:
        pytest_cmd.extend(["-m", "integration"])
    elif not args.slow:
        pytest_cmd.extend(["-m", "not slow"])
    
    # 添加特定文件
    if args.file:
        pytest_cmd.append(f"tests/{args.file}")
    
    # 添加特定函數
    if args.function:
        pytest_cmd.extend(["-k", args.function])
    
    # 如果沒有指定特定文件，運行所有測試
    if not args.file:
        pytest_cmd.append("tests/")
    
    # 運行測試
    success = run_command(pytest_cmd, "運行測試")
    
    if success:
        print("\n✅ 所有測試通過！")
        
        if args.coverage or args.html:
            print("\n📊 覆蓋率報告已生成")
            if args.html:
                print("🌐 HTML 報告位於: htmlcov/index.html")
    else:
        print("\n❌ 測試失敗")
        sys.exit(1)


if __name__ == "__main__":
    main() 