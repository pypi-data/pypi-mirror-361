#!/bin/bash

# AIS - AI智能终端助手
# 卸载脚本 - 完全清理所有相关文件和配置
# 
# 使用方法: curl -sSL https://raw.githubusercontent.com/kangvcar/ais/main/scripts/uninstall.sh | bash

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_step() {
    echo -e "${BLUE}📋 第$1步: $2${NC}"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检测用户的 shell 配置文件
detect_shell_config() {
    shell_name=$(basename "$SHELL")
    case $shell_name in
        zsh)
            echo "$HOME/.zshrc"
            ;;
        bash)
            if [ -f "$HOME/.bashrc" ]; then
                echo "$HOME/.bashrc"
            else
                echo "$HOME/.bash_profile"
            fi
            ;;
        *)
            echo "$HOME/.bashrc"
            ;;
    esac
}

# 确认卸载
confirm_uninstall() {
    echo "================================================"
    echo "         AIS - AI 智能终端助手 卸载器"
    echo "================================================"
    echo
    print_warning "此脚本将完全移除 AIS 及其配置文件"
    print_info "将要删除的内容："
    print_info "  • AIS 应用程序"
    print_info "  • Shell 集成配置"
    print_info "  • 配置文件和数据库"
    print_info "  • 系统集成脚本"
    echo
    
    read -p "❓ 确定要卸载 AIS 吗？(y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "取消卸载"
        exit 0
    fi
    
    echo
}

# 移除 AIS 应用程序
remove_ais_app() {
    print_step 1 "移除 AIS 应用程序"
    
    # 检查 pipx 安装（用户级和全局级）
    if command_exists pipx; then
        print_info "检查 pipx 安装..."
        
        # 检查用户级 pipx 安装
        if pipx list 2>/dev/null | grep -q "ais-terminal"; then
            print_info "发现 pipx 用户级安装，正在卸载..."
            pipx uninstall ais-terminal
            print_success "pipx 用户级安装已卸载"
        else
            print_info "未发现 pipx 用户级安装"
        fi
        
        # 检查全局 pipx 安装
        if command -v sudo >/dev/null 2>&1; then
            if sudo PIPX_HOME=/opt/pipx pipx list 2>/dev/null | grep -q "ais-terminal"; then
                print_info "发现 pipx 全局安装，正在卸载..."
                read -p "是否卸载 pipx 全局安装？(y/N): " -r
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    sudo PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx uninstall ais-terminal
                    print_success "pipx 全局安装已卸载"
                fi
            else
                print_info "未发现 pipx 全局安装"
            fi
        fi
    else
        print_info "pipx 未安装，跳过 pipx 检查"
    fi
    
    # 检查 pip 安装
    if command_exists pip; then
        if pip show ais-terminal >/dev/null 2>&1; then
            print_info "发现 pip 安装，正在卸载..."
            read -p "是否卸载 pip 安装？(y/N): " -r
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                pip uninstall -y ais-terminal
                print_success "pip 安装已卸载"
            fi
        fi
    fi
    
    # 检查系统级全局安装
    if [ -f "/usr/local/bin/ais" ]; then
        print_info "发现系统级全局安装..."
        read -p "是否删除系统级全局安装？(y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo rm -f /usr/local/bin/ais
            print_success "系统级全局安装已移除"
        fi
    fi
    
    # 检查是否还有残留
    if command_exists ais; then
        ais_path=$(which ais)
        print_warning "发现残留的 AIS: $ais_path"
        read -p "是否删除？(y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [[ "$ais_path" == "/usr/local/bin/ais" ]] || [[ "$ais_path" == "/opt/"* ]]; then
                sudo rm -f "$ais_path"
            else
                rm -f "$ais_path"
            fi
            print_success "残留文件已删除"
        fi
    fi
}

# 移除 Shell 集成
remove_shell_integration() {
    print_step 2 "移除 Shell 集成"
    
    shell_config=$(detect_shell_config)
    print_info "Shell 配置文件: $shell_config"
    
    if [ -f "$shell_config" ]; then
        # 备份配置文件
        cp "$shell_config" "${shell_config}.backup.$(date +%Y%m%d_%H%M%S)"
        print_info "已创建配置文件备份"
        
        # 移除 AIS 集成配置
        if grep -q "# START AIS INTEGRATION" "$shell_config"; then
            print_info "移除 shell 集成配置..."
            sed -i '/# START AIS INTEGRATION/,/# END AIS INTEGRATION/d' "$shell_config"
            print_success "Shell 集成配置已移除"
        else
            print_info "未发现 shell 集成配置"
        fi
    else
        print_info "Shell 配置文件不存在"
    fi
}

# 移除配置文件和数据
remove_config_and_data() {
    print_step 3 "移除配置文件和数据"
    
    # AIS 配置目录
    config_dir="$HOME/.config/ais"
    if [ -d "$config_dir" ]; then
        print_info "移除配置目录: $config_dir"
        rm -rf "$config_dir"
        print_success "配置目录已删除"
    else
        print_info "配置目录不存在"
    fi
    
    # AIS 数据目录
    data_dir="$HOME/.local/share/ais"
    if [ -d "$data_dir" ]; then
        print_info "移除数据目录: $data_dir"
        rm -rf "$data_dir"
        print_success "数据目录已删除"
    else
        print_info "数据目录不存在"
    fi
    
    # 移除自动配置标记文件
    auto_setup_marker="$HOME/.config/ais/.auto_setup_done"
    if [ -f "$auto_setup_marker" ]; then
        rm -f "$auto_setup_marker"
        print_info "自动配置标记已清除"
    fi
    
    # 检查其他可能的位置
    other_locations=(
        "$HOME/.ais"
        "/usr/local/share/ais"
        "/opt/ais"
    )
    
    for location in "${other_locations[@]}"; do
        if [ -d "$location" ]; then
            print_info "发现其他位置的文件: $location"
            read -p "是否删除？(y/N): " -r
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                if [[ "$location" == "/usr/local/share/ais" ]] || [[ "$location" == "/opt/ais" ]]; then
                    sudo rm -rf "$location"
                else
                    rm -rf "$location"
                fi
                print_success "已删除: $location"
            fi
        fi
    done
}

# 清理系统集成
remove_system_integration() {
    print_step 4 "清理系统集成"
    
    # 移除系统级集成脚本
    if [ -f "/usr/local/share/ais-integration.sh" ]; then
        print_info "移除系统集成脚本..."
        sudo rm -f /usr/local/share/ais-integration.sh
        print_success "系统集成脚本已移除"
    fi
    
    # 移除可能的符号链接
    if [ -L "/usr/local/bin/ais" ]; then
        print_info "移除符号链接..."
        sudo rm -f /usr/local/bin/ais
        print_success "符号链接已移除"
    fi
}

# 验证卸载
verify_uninstall() {
    print_step 5 "验证卸载"
    
    errors=0
    
    # 检查命令是否还存在
    if command_exists ais; then
        print_warning "AIS 命令仍然存在: $(which ais)"
        errors=$((errors + 1))
    else
        print_success "AIS 命令已不存在"
    fi
    
    # 检查配置目录
    if [ -d "$HOME/.config/ais" ]; then
        print_warning "配置目录仍然存在: $HOME/.config/ais"
        errors=$((errors + 1))
    else
        print_success "配置目录已清理"
    fi
    
    # 检查数据目录
    if [ -d "$HOME/.local/share/ais" ]; then
        print_warning "数据目录仍然存在: $HOME/.local/share/ais"
        errors=$((errors + 1))
    else
        print_success "数据目录已清理"
    fi
    
    if [ $errors -eq 0 ]; then
        print_success "卸载验证通过"
    else
        print_warning "发现 $errors 个残留项目，可能需要手动清理"
    fi
}

# 显示完成信息
show_completion() {
    echo
    print_success "🎉 AIS 卸载完成！"
    echo
    print_info "📋 重要提醒:"
    print_info "  1. 请重新加载 shell 配置: source ~/.bashrc"
    print_info "  2. 或者重启终端以使更改生效"
    echo
    print_info "💾 备份文件:"
    shell_config=$(detect_shell_config)
    backup_files=$(ls "${shell_config}.backup."* 2>/dev/null || true)
    if [ -n "$backup_files" ]; then
        print_info "  Shell 配置备份: $backup_files"
        print_info "  如需恢复，可以使用这些备份文件"
    fi
    echo
    print_info "🙏 感谢使用 AIS！"
    echo
}

# 主卸载流程
main() {
    # 确认卸载
    confirm_uninstall
    
    # 执行卸载步骤
    remove_ais_app
    remove_shell_integration
    remove_config_and_data
    remove_system_integration
    
    # 验证和完成
    verify_uninstall
    show_completion
}

# 处理命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            echo "AIS 卸载脚本"
            echo
            echo "用法: $0 [选项]"
            echo
            echo "选项:"
            echo "  --help          显示此帮助信息"
            echo
            echo "快速卸载:"
            echo "  curl -sSL https://raw.githubusercontent.com/kangvcar/ais/main/uninstall.sh | bash"
            exit 0
            ;;
        *)
            print_error "未知选项: $1"
            print_info "使用 --help 查看帮助"
            exit 1
            ;;
    esac
done

# 运行主程序
main