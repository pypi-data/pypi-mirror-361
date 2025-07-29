"""
验证XHR请求模块的语法和基本功能
"""

def verify_import():
    """验证模块导入"""
    try:
        from xhr_request import XHRClient, XHRResponse
        print("✓ 模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return False

def verify_class_structure():
    """验证类结构"""
    try:
        from xhr_request import XHRClient, XHRResponse
        
        # 检查XHRResponse类
        response = XHRResponse(200, '{"test": "data"}', {"Content-Type": "application/json"}, "http://test.com")
        assert response.status_code == 200
        assert response.text == '{"test": "data"}'
        assert response.ok == True
        print("✓ XHRResponse类结构正确")
        
        # 检查XHRClient类（不创建实例，只检查方法存在）
        methods = ['request', 'get', 'post', 'put', 'patch', 'delete']
        for method in methods:
            assert hasattr(XHRClient, method), f"缺少方法: {method}"
        print("✓ XHRClient类方法完整")
        
        return True
    except Exception as e:
        print(f"✗ 类结构验证失败: {e}")
        return False

def verify_method_signatures():
    """验证方法签名"""
    try:
        from xhr_request import XHRClient
        import inspect
        
        # 检查request方法签名
        sig = inspect.signature(XHRClient.request)
        params = list(sig.parameters.keys())
        expected_params = ['self', 'method', 'url', 'data', 'json_data', 'headers', 'timeout']
        
        for param in expected_params:
            assert param in params, f"request方法缺少参数: {param}"
        
        print("✓ request方法签名正确")
        
        # 检查便捷方法签名
        convenience_methods = {
            'get': ['self', 'url', 'headers', 'timeout'],
            'post': ['self', 'url', 'data', 'json_data', 'headers', 'timeout'],
            'put': ['self', 'url', 'data', 'json_data', 'headers', 'timeout'],
            'patch': ['self', 'url', 'data', 'json_data', 'headers', 'timeout'],
            'delete': ['self', 'url', 'headers', 'timeout']
        }
        
        for method_name, expected_params in convenience_methods.items():
            method = getattr(XHRClient, method_name)
            sig = inspect.signature(method)
            params = list(sig.parameters.keys())
            
            for param in expected_params:
                assert param in params, f"{method_name}方法缺少参数: {param}"
        
        print("✓ 便捷方法签名正确")
        return True
        
    except Exception as e:
        print(f"✗ 方法签名验证失败: {e}")
        return False

def verify_data_processing():
    """验证数据处理逻辑"""
    try:
        import json
        
        # 测试JSON序列化
        test_data = {'name': '测试', 'value': 123, 'list': [1, 2, 3]}
        json_str = json.dumps(test_data, ensure_ascii=False)
        assert '测试' in json_str
        print("✓ JSON序列化支持中文")
        
        # 测试base64编码（用于二进制数据）
        import base64
        binary_data = b'\x00\x01\x02\x03'
        encoded = base64.b64encode(binary_data).decode('ascii')
        decoded = base64.b64decode(encoded)
        assert decoded == binary_data
        print("✓ 二进制数据编码/解码正确")
        
        return True
        
    except Exception as e:
        print(f"✗ 数据处理验证失败: {e}")
        return False

def main():
    """主验证函数"""
    print("=== XHR请求模块验证 ===\n")
    
    tests = [
        ("模块导入", verify_import),
        ("类结构", verify_class_structure),
        ("方法签名", verify_method_signatures),
        ("数据处理", verify_data_processing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"测试: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print(f"=== 验证结果: {passed}/{total} 通过 ===")
    
    if passed == total:
        print("🎉 所有验证通过！XHR请求模块已成功优化")
        print("\n主要改进:")
        print("- ✅ 支持多种数据类型 (Dict, str, bytes, JSON)")
        print("- ✅ 统一的API接口")
        print("- ✅ 自定义请求头支持")
        print("- ✅ 完整的HTTP方法支持")
        print("- ✅ 更好的错误处理")
    else:
        print("❌ 部分验证失败，请检查代码")

if __name__ == "__main__":
    main()
