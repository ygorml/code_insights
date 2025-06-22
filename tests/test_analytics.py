import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics import (
    ClassInfo, get_project_metrics, get_ck_metrics,
    get_project_statistics, analyze_ast_class,
    calculate_wmc, calculate_dit, calculate_noc,
    calculate_rfc, calculate_cbo, calculate_lcom
)


class TestClassInfo:
    def test_class_info_initialization(self):
        """Test ClassInfo initialization with proper defaults."""
        class_info = ClassInfo("TestClass")
        assert class_info.name == "TestClass"
        assert class_info.methods == []
        assert class_info.attributes == set()
        assert class_info.base_classes == []
        assert class_info.children == []
        assert class_info.calls == set()
        assert class_info.called_by == set()


class TestProjectMetrics:
    def setUp(self):
        """Create temporary directory with sample Python files for testing."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create sample Python file
        sample_code = '''
class SampleClass:
    def __init__(self):
        self.attribute = 0
    
    def method1(self):
        return self.attribute
    
    def method2(self):
        return self.method1() + 1

def standalone_function():
    return 42
'''
        with open(os.path.join(self.temp_dir, 'sample.py'), 'w') as f:
            f.write(sample_code)
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_get_project_metrics_valid_path(self):
        """Test get_project_metrics with valid project path."""
        self.setUp()
        try:
            with patch('analytics.raw.analyze') as mock_analyze:
                mock_analyze.return_value = {
                    'loc': 10,
                    'lloc': 8,
                    'sloc': 7,
                    'comments': 2,
                    'multi': 1
                }
                
                result = get_project_metrics(self.temp_dir)
                assert isinstance(result, dict)
                assert 'sample.py' in result
        finally:
            self.tearDown()
    
    def test_get_project_metrics_invalid_path(self):
        """Test get_project_metrics with invalid path."""
        result = get_project_metrics("/nonexistent/path")
        assert result == {}
    
    def test_get_ck_metrics_valid_path(self):
        """Test get_ck_metrics with valid project path."""
        self.setUp()
        try:
            result = get_ck_metrics(self.temp_dir)
            assert isinstance(result, dict)
            if result:  # If there are any files processed
                for file_path, classes in result.items():
                    assert isinstance(classes, dict)
        finally:
            self.tearDown()


class TestCKMetricsCalculation:
    def test_calculate_wmc(self):
        """Test Weighted Methods per Class calculation."""
        class_info = ClassInfo("TestClass")
        class_info.methods = ['method1', 'method2', 'method3']
        
        wmc = calculate_wmc(class_info)
        assert wmc == 3
    
    def test_calculate_dit_no_inheritance(self):
        """Test Depth of Inheritance Tree with no inheritance."""
        class_info = ClassInfo("TestClass")
        classes = {'TestClass': class_info}
        
        dit = calculate_dit(class_info, classes)
        assert dit == 0
    
    def test_calculate_dit_with_inheritance(self):
        """Test Depth of Inheritance Tree with inheritance."""
        parent = ClassInfo("Parent")
        child = ClassInfo("Child")
        child.base_classes = ['Parent']
        classes = {'Parent': parent, 'Child': child}
        
        dit = calculate_dit(child, classes)
        assert dit == 1
    
    def test_calculate_noc(self):
        """Test Number of Children calculation."""
        class_info = ClassInfo("TestClass")
        class_info.children = ['Child1', 'Child2']
        
        noc = calculate_noc(class_info)
        assert noc == 2
    
    def test_calculate_rfc(self):
        """Test Response for a Class calculation."""
        class_info = ClassInfo("TestClass")
        class_info.methods = ['method1', 'method2']
        class_info.calls = {'external_call1', 'external_call2', 'external_call3'}
        
        rfc = calculate_rfc(class_info)
        assert rfc == 5  # 2 methods + 3 external calls
    
    def test_calculate_cbo(self):
        """Test Coupling Between Objects calculation."""
        class_info = ClassInfo("TestClass")
        class_info.calls = {'Class1', 'Class2'}
        class_info.called_by = {'Class3'}
        
        cbo = calculate_cbo(class_info)
        assert cbo == 3  # 2 calls + 1 called_by
    
    def test_calculate_lcom_no_methods(self):
        """Test LCOM calculation with no methods."""
        class_info = ClassInfo("TestClass")
        
        lcom = calculate_lcom(class_info)
        assert lcom == 0
    
    def test_calculate_lcom_with_methods(self):
        """Test LCOM calculation with methods."""
        class_info = ClassInfo("TestClass")
        class_info.methods = ['method1', 'method2']
        class_info.attributes = {'attr1', 'attr2'}
        
        # Mock method-attribute relationships
        with patch('analytics.analyze_method_attribute_usage') as mock_usage:
            mock_usage.return_value = {'method1': {'attr1'}, 'method2': {'attr2'}}
            lcom = calculate_lcom(class_info)
            assert isinstance(lcom, (int, float))


class TestProjectStatistics:
    def test_get_project_statistics_empty_metrics(self):
        """Test get_project_statistics with empty metrics."""
        result = get_project_statistics({}, "main")
        expected_keys = ['total_files', 'total_loc', 'total_lloc', 'total_sloc', 
                        'total_comments', 'mean_complexity', 'mean_maintainability']
        
        for key in expected_keys:
            assert key in result
        assert result['total_files'] == 0
    
    def test_get_project_statistics_with_metrics(self):
        """Test get_project_statistics with valid metrics."""
        metrics_data = {
            'file1.py': {
                'loc': 100,
                'lloc': 80,
                'sloc': 75,
                'comments': 10,
                'complexity': 5.0,
                'maintainability': 70.5
            },
            'file2.py': {
                'loc': 50,
                'lloc': 40,
                'sloc': 35,
                'comments': 5,
                'complexity': 3.0,
                'maintainability': 80.0
            }
        }
        
        result = get_project_statistics(metrics_data, "main")
        
        assert result['total_files'] == 2
        assert result['total_loc'] == 150
        assert result['total_lloc'] == 120
        assert result['total_sloc'] == 110
        assert result['total_comments'] == 15
        assert result['mean_complexity'] == 4.0
        assert result['mean_maintainability'] == 75.25


class TestASTAnalysis:
    def test_analyze_ast_class_simple(self):
        """Test AST analysis of a simple class."""
        code = '''
class SimpleClass:
    def __init__(self):
        self.attr = 0
    
    def method(self):
        return self.attr
'''
        import ast
        tree = ast.parse(code)
        
        result = analyze_ast_class(tree.body[0], 'SimpleClass')
        
        assert isinstance(result, ClassInfo)
        assert result.name == 'SimpleClass'
        assert len(result.methods) >= 2  # __init__ and method
        assert 'attr' in result.attributes
    
    def test_analyze_ast_class_with_inheritance(self):
        """Test AST analysis of a class with inheritance."""
        code = '''
class ChildClass(ParentClass):
    def child_method(self):
        pass
'''
        import ast
        tree = ast.parse(code)
        
        result = analyze_ast_class(tree.body[0], 'ChildClass')
        
        assert isinstance(result, ClassInfo)
        assert result.name == 'ChildClass'
        assert 'ParentClass' in result.base_classes


if __name__ == '__main__':
    pytest.main([__file__])