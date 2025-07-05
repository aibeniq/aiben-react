from typing import Literal
from sqlmodel import Field, SQLModel


class TestModel(SQLModel):
    search_mode: Literal["vector", "full_scan"] = Field(default="vector")


# Test instantiation
test = TestModel()
print(f"Default search_mode: {test.search_mode}")

test2 = TestModel(search_mode="full_scan")
print(f"Custom search_mode: {test2.search_mode}")

print("✅ Literal with Field works correctly!")
