"""
結構化輸出和模式定義單元測試
"""

import pytest
import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError

from ollama_flow.schemas import StructuredOutput


class PersonModel(BaseModel):
    """測試用的人員模型"""
    name: str = Field(..., description="姓名")
    age: int = Field(..., description="年齡", ge=0, le=120)
    email: Optional[str] = Field(None, description="電子郵件")
    skills: List[str] = Field(default_factory=list, description="技能列表")
    is_active: bool = Field(True, description="是否活躍")


class CompanyModel(BaseModel):
    """測試用的公司模型"""
    name: str = Field(..., description="公司名稱")
    employees: List[PersonModel] = Field(..., description="員工列表")
    founded_year: int = Field(..., description="成立年份", ge=1800, le=2024)
    address: Dict[str, str] = Field(..., description="地址信息")


class NestedModel(BaseModel):
    """測試用的嵌套模型"""
    metadata: Dict[str, Any] = Field(..., description="元數據")
    items: List[Dict[str, Any]] = Field(default_factory=list, description="項目列表")


class TestStructuredOutput:
    """StructuredOutput 類別測試"""
    
    def test_simple_schema_generation(self):
        """測試簡單模型的模式生成"""
        schema = StructuredOutput.from_pydantic(PersonModel)
        
        assert "type" in schema
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        
        # 檢查必要欄位
        assert "name" in schema["required"]
        assert "age" in schema["required"]
        assert "email" not in schema["required"]
        
        # 檢查屬性
        properties = schema["properties"]
        assert "name" in properties
        assert "age" in properties
        assert "email" in properties
        assert "skills" in properties
        assert "is_active" in properties
        
        # 檢查屬性類型
        assert properties["name"]["type"] == "string"
        assert properties["age"]["type"] == "integer"
        assert properties["skills"]["type"] == "array"
        assert properties["is_active"]["type"] == "boolean"
        
    def test_complex_schema_generation(self):
        """測試複雜模型的模式生成"""
        schema = StructuredOutput.from_pydantic(CompanyModel)
        
        assert schema["type"] == "object"
        properties = schema["properties"]
        
        # 檢查員工列表
        assert "employees" in properties
        employees_prop = properties["employees"]
        assert employees_prop["type"] == "array"
        assert "items" in employees_prop
        
        # 檢查員工項目的結構（使用 $ref）
        employee_schema = employees_prop["items"]
        assert "$ref" in employee_schema
        assert employee_schema["$ref"] == "#/$defs/PersonModel"
        
        # 檢查定義部分
        assert "$defs" in schema
        assert "PersonModel" in schema["$defs"]
        person_def = schema["$defs"]["PersonModel"]
        assert "name" in person_def["properties"]
        assert "age" in person_def["properties"]
        
        # 檢查地址字典
        assert "address" in properties
        address_prop = properties["address"]
        assert address_prop["type"] == "object"
        
    def test_schema_with_constraints(self):
        """測試帶約束的模式生成"""
        schema = StructuredOutput.from_pydantic(PersonModel)
        
        properties = schema["properties"]
        age_prop = properties["age"]
        
        # 檢查年齡約束
        assert age_prop["minimum"] == 0
        assert age_prop["maximum"] == 120
        
    def test_custom_schema_generation(self):
        """測試自定義模式生成"""
        schema = StructuredOutput.from_pydantic(PersonModel)
        
        # 檢查模式包含基本結構
        assert "title" in schema
        assert "description" in schema
        assert schema["title"] == "PersonModel"
        assert schema["description"] == "測試用的人員模型"
        
    def test_get_json_schema_string(self):
        """測試獲取 JSON 模式字符串"""
        schema = StructuredOutput.from_pydantic(PersonModel)
        schema_str = json.dumps(schema)
        
        # 確認是有效的 JSON
        parsed_schema = json.loads(schema_str)
        assert parsed_schema["type"] == "object"
        assert "properties" in parsed_schema
        
    def test_validate_response_success(self):
        """測試成功驗證回應"""
        valid_data = {
            "name": "張三",
            "age": 30,
            "email": "zhangsan@example.com",
            "skills": ["Python", "JavaScript"],
            "is_active": True
        }
        
        result = PersonModel.model_validate(valid_data)
        assert isinstance(result, PersonModel)
        assert result.name == "張三"
        assert result.age == 30
        assert result.email == "zhangsan@example.com"
        assert result.skills == ["Python", "JavaScript"]
        assert result.is_active is True
        
    def test_validate_response_with_optional_fields(self):
        """測試包含可選欄位的回應驗證"""
        minimal_data = {
            "name": "李四",
            "age": 25
        }
        
        result = PersonModel.model_validate(minimal_data)
        assert isinstance(result, PersonModel)
        assert result.name == "李四"
        assert result.age == 25
        assert result.email is None
        assert result.skills == []
        assert result.is_active is True  # 預設值
        
    def test_validate_response_missing_required_field(self):
        """測試缺少必要欄位的回應驗證"""
        invalid_data = {
            "age": 30,
            "email": "test@example.com"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PersonModel.model_validate(invalid_data)
        
        assert "Field required" in str(exc_info.value)
        
    def test_validate_response_invalid_type(self):
        """測試無效類型的回應驗證"""
        invalid_data = {
            "name": "王五",
            "age": "不是數字",  # 應該是整數
            "skills": "不是列表"  # 應該是列表
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PersonModel.model_validate(invalid_data)
        
        assert "Input should be a valid integer" in str(exc_info.value)
        
    def test_validate_response_constraint_violation(self):
        """測試約束違反的回應驗證"""
        invalid_data = {
            "name": "趙六",
            "age": 150  # 超過最大值
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PersonModel.model_validate(invalid_data)
        
        assert "Input should be less than or equal to 120" in str(exc_info.value)
        
    def test_parse_json_response_success(self):
        """測試成功解析 JSON 回應"""
        json_response = '''
        {
            "name": "錢七",
            "age": 28,
            "email": "qianqi@example.com",
            "skills": ["Python", "Go"],
            "is_active": false
        }
        '''
        
        result = StructuredOutput.parse_response(json_response, PersonModel)
        assert isinstance(result, PersonModel)
        assert result.name == "錢七"
        assert result.age == 28
        assert result.is_active is False
        
    def test_parse_json_response_invalid_json(self):
        """測試解析無效 JSON 回應"""
        invalid_json = '{"name": "孫八", "age": 35'  # 缺少結束括號
        
        with pytest.raises(ValueError) as exc_info:
            StructuredOutput.parse_response(invalid_json, PersonModel)
        
        assert "Unable to parse JSON response" in str(exc_info.value)
        
    def test_parse_json_response_validation_error(self):
        """測試解析驗證錯誤的 JSON 回應"""
        invalid_json = '''
        {
            "name": "周九",
            "age": -5,
            "skills": "錯誤的類型"
        }
        '''
        
        with pytest.raises(ValueError) as exc_info:
            StructuredOutput.parse_response(invalid_json, PersonModel)
        
        assert "Unable to validate response data" in str(exc_info.value)
            
    def test_nested_model_schema(self):
        """測試嵌套模型的模式生成"""
        schema = StructuredOutput.from_pydantic(CompanyModel)
        
        # 檢查頂層屬性
        properties = schema["properties"]
        assert "name" in properties
        assert "employees" in properties
        assert "founded_year" in properties
        assert "address" in properties
        
        # 檢查員工列表的嵌套結構
        employees_prop = properties["employees"]
        assert employees_prop["type"] == "array"
        employee_item = employees_prop["items"]
        assert "$ref" in employee_item
        assert employee_item["$ref"] == "#/$defs/PersonModel"
        
        # 檢查員工屬性在定義中
        person_def = schema["$defs"]["PersonModel"]
        employee_props = person_def["properties"]
        assert "name" in employee_props
        assert "age" in employee_props
        assert "skills" in employee_props
        
    def test_dict_type_schema(self):
        """測試字典類型的模式生成"""
        schema = StructuredOutput.from_pydantic(NestedModel)
        properties = schema["properties"]
        
        # 檢查元數據字典
        metadata_prop = properties["metadata"]
        assert metadata_prop["type"] == "object"
        
        # 檢查項目列表
        items_prop = properties["items"]
        assert items_prop["type"] == "array"
        
    def test_schema_json_serialization(self):
        """測試模式的 JSON 序列化"""
        schema = StructuredOutput.from_pydantic(PersonModel)
        # schema already generated
        
        # 確認可以序列化為 JSON
        json_str = json.dumps(schema)
        assert isinstance(json_str, str)
        
        # 確認可以反序列化
        deserialized = json.loads(json_str)
        assert deserialized == schema
        
    def test_multiple_models_independence(self):
        """測試多個模型的獨立性"""
        person_schema = StructuredOutput.from_pydantic(PersonModel)
        company_schema = StructuredOutput.from_pydantic(CompanyModel)
        
        # 確認不同模型產生不同的模式
        assert person_schema != company_schema
        assert "employees" not in person_schema["properties"]
        assert "name" in person_schema["properties"]
        assert "employees" in company_schema["properties"]
        
    def test_schema_caching(self):
        """測試模式快取"""
        # 多次獲取模式
        schema1 = StructuredOutput.from_pydantic(PersonModel)
        schema2 = StructuredOutput.from_pydantic(PersonModel)
        
        # 應該是相同的對象（如果有快取）或相同的內容
        assert schema1 == schema2
        
    def test_model_with_default_values(self):
        """測試包含預設值的模型"""
        schema = StructuredOutput.from_pydantic(PersonModel)
        
        # 測試只提供必要欄位
        minimal_data = {
            "name": "預設測試",
            "age": 25
        }
        
        result = PersonModel.model_validate(minimal_data)
        assert result.skills == []  # 預設為空列表
        assert result.is_active is True  # 預設為 True
        assert result.email is None  # 預設為 None
        
    def test_schema_with_descriptions(self):
        """測試模式中的描述"""
        schema = StructuredOutput.from_pydantic(PersonModel)
        properties = schema["properties"]
        
        # 檢查描述是否包含在模式中
        assert "description" in properties["name"]
        assert "description" in properties["age"]
        assert "description" in properties["skills"]
        
        # 檢查具體的描述內容
        assert properties["name"]["description"] == "姓名"
        assert properties["age"]["description"] == "年齡"
        assert properties["skills"]["description"] == "技能列表"


class TestEdgeCases:
    """邊界情況測試"""
    
    def test_empty_model(self):
        """測試空模型"""
        class EmptyModel(BaseModel):
            pass
        
        schema = StructuredOutput.from_pydantic(EmptyModel)
        assert schema["type"] == "object"
        assert "properties" in schema
        assert len(schema["properties"]) == 0
        
    def test_model_with_only_optional_fields(self):
        """測試只有可選欄位的模型"""
        class OptionalModel(BaseModel):
            optional_field: Optional[str] = None
            default_field: str = "default"
        
        schema = StructuredOutput.from_pydantic(OptionalModel)
        assert len(schema.get("required", [])) == 0
        assert "optional_field" in schema["properties"]
        assert "default_field" in schema["properties"]
        
    def test_very_nested_model(self):
        """測試深度嵌套模型"""
        class Level3(BaseModel):
            value: str
            
        class Level2(BaseModel):
            level3: Level3
            
        class Level1(BaseModel):
            level2: Level2
            
        schema = StructuredOutput.from_pydantic(Level1)
        # schema already generated
        
        # 驗證能夠處理深度嵌套
        assert schema["type"] == "object"
        level2_prop = schema["properties"]["level2"]
        assert "$ref" in level2_prop
        assert level2_prop["$ref"] == "#/$defs/Level2"
        
        # 檢查定義部分
        assert "$defs" in schema
        assert "Level2" in schema["$defs"]
        assert "Level3" in schema["$defs"]
        level2_def = schema["$defs"]["Level2"]
        level3_def = schema["$defs"]["Level3"]
        assert "value" in level3_def["properties"] 