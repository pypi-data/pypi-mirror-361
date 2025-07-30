# Generic AI Assistant Project Structure

## Directory Structure

Follow strict vertical slice architecture

```
project/
├── .ai/                            # AI assistant configuration
│   ├── commands/                   # Custom automation commands
│   │   ├── generate-spec.md        # Specification generation logic
│   │   └── execute-spec.md         # Specification execution logic
│   └── settings.json              # AI assistant permissions and preferences
│
├── specs/                          # Project Specification Documents
│   ├── templates/                  # Reusable specification templates
│   │   └── spec_base.md           # Base template structure
│   └── [feature-name].md          # Generated specifications
│
├── examples/                       # Code patterns and references
│   ├── README.md                  # Example documentation
│   ├── patterns/                  # Reusable design patterns
│   └── implementations/           # Reference implementations
│
├── docs/                          # Project documentation
│   ├── chat-history/              # AI conversation logs
│   │   ├── README.md              # Session index
│   │   └── YYYY-MM-DD_topic.md    # Timestamped sessions
│   └── workflows/                 # Development workflows
│
├── AI_GUIDELINES.md               # Global AI assistant rules and best practices
├── FEATURE_REQUEST.md             # Feature request template
└── README.md                      # Project overview and setup
```

## Key Improvements

✅ **AI-Agnostic**: Works with Claude, GPT, Gemini, or any AI assistant  
✅ **Generic Terms**: "specs" instead of "PRPs", "guidelines" instead of "CLAUDE.md"  
✅ **Industry Standard**: Uses common software development terminology  
✅ **Documentation Focus**: Added dedicated `docs/` directory  
✅ **Workflow Support**: Includes chat history and workflow documentation  
✅ **Scalable**: Structure grows with project complexity  

## Directory Purpose

| Directory | Purpose |
|-----------|---------|
| `.ai/` | AI assistant configuration and custom commands |
| `specs/` | Project specifications and requirements |
| `examples/` | Code patterns and reference implementations |
| `docs/` | All project documentation including AI chat logs |
| Root files | Core configuration and entry points |

## Benefits

This structure works across different AI tools, programming languages, and project types while maintaining clear organization and traceability.

### Flexibility
- **Multi-AI Support**: Configuration works with any AI assistant
- **Language Agnostic**: Suitable for Python, JavaScript, Go, or any language
- **Project Scale**: Adapts from small scripts to enterprise applications

### Organization
- **Clear Separation**: Each directory has a specific, well-defined purpose
- **Searchable**: Consistent naming makes finding files intuitive
- **Maintainable**: Structure supports long-term project evolution

### Traceability
- **Chat History**: Complete record of AI-assisted development decisions
- **Specifications**: Detailed requirements and implementation plans
- **Examples**: Reference patterns for consistent development practices

## Implementation Notes

1. **Start Simple**: Begin with just the directories you need
2. **Add Gradually**: Expand structure as project complexity grows
3. **Customize**: Adapt naming conventions to match your team's preferences
4. **Document**: Keep README files updated in each directory
5. **Automate**: Use AI commands to maintain consistency across projects