from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.models import Message
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    return True

def invoke_llm(llm, prompt, variables=None):
    """
    Unified function to invoke either a ReplicateWrapper or LangChain LLM.
    - llm: The LLM instance.
    - prompt: Either a string (for Replicate) or a LangChain ChatPromptTemplate.
    - variables: dict of variables for the prompt (for LangChain).
    Returns the response content as a string.
    """
    # ReplicateWrapper: expects a formatted string prompt
    if hasattr(llm, '__class__') and 'ReplicateWrapper' in llm.__class__.__name__:
        if variables:
            prompt_text = prompt.format(**variables)
        else:
            prompt_text = prompt
        return llm.invoke(prompt_text)
    else:
        # LangChain: expects a ChatPromptTemplate and variables
        if variables is None:
            variables = {}
        if hasattr(prompt, "from_template"):
            # If prompt is a template, build the chain
            section_prompt = prompt.from_template(prompt.template)
            chain = section_prompt | llm
            response = chain.invoke(variables)
            return response.content
        elif hasattr(prompt, "format_prompt"):
            # If prompt is already a ChatPromptTemplate
            chain = prompt | llm
            response = chain.invoke(variables)
            return response.content
        else:
            # If prompt is a plain string, just pass as-is
            return llm(prompt)
