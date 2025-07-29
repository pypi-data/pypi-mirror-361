# 🏗️ AWS Well-Architected MCP Server

A powerful Model Context Protocol (MCP) server that provides seamless integration with AWS Well-Architected Framework for AI assistants like GitHub Copilot, AWS Q, Cursor, and other modern IDEs.

## 🚀 Features

- **Complete AWS Well-Architected Integration**: Access all major Well-Architected Framework capabilities
- **AI Assistant Ready**: Works with GitHub Copilot, AWS Q, Cursor, and other MCP-compatible tools
- **Easy Configuration**: Simple setup for any IDE or AI assistant
- **Secure AWS Access**: Uses your existing AWS credentials and profiles
- **Rich Functionality**: 
  - List and explore Well-Architected lenses
  - Manage workloads and reviews
  - Access improvement recommendations
  - Generate reports
  - Track milestones

## 📋 Prerequisites

- Python 3.11+
- AWS CLI configured (`aws configure`)
- Active AWS credentials with Well-Architected permissions
- An IDE or AI assistant that supports MCP (VS Code, Cursor, etc.)

## 🛠️ Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install wellarchitected-mcp-server
```

### Option 2: Install with uvx (Preferred for AI assistants)

```bash
uvx wellarchitected-mcp-server@latest
```

### Option 3: Development Installation

```bash
git clone <repository-url>
cd wellarchitected-mcp-server
pip install -e .
```

## ⚙️ Configuration

### AWS Credentials Setup

Ensure your AWS credentials are configured:

```bash
aws configure
# or
export AWS_PROFILE=your-profile
export AWS_REGION=us-east-1
```

### Required AWS Permissions

Your AWS credentials need the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "wellarchitected:List*",
                "wellarchitected:Get*",
                "wellarchitected:Create*",
                "wellarchitected:Update*"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🔧 IDE and AI Assistant Configuration

### GitHub Copilot (VS Code)

Add to your `.vscode/settings.json`:

```json
{
  "github.copilot.chat.experimental.modelContextProtocol.servers": {
    "aws-wellarchitected": {
      "command": "uvx",
      "args": ["wellarchitected-mcp-server@latest"],
      "env": {
        "AWS_PROFILE": "default",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

### AWS Q (if supporting MCP)

```json
{
  "mcp_servers": {
    "aws-wellarchitected": {
      "command": "wellarch-mcp",
      "env": {
        "AWS_PROFILE": "default",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

### Cursor IDE

Add to your Cursor configuration:

```json
{
  "mcp": {
    "servers": {
      "aws-wellarchitected": {
        "command": "uvx",
        "args": ["wellarchitected-mcp-server@latest"],
        "env": {
          "AWS_PROFILE": "default",
          "AWS_REGION": "us-east-1"
        }
      }
    }
  }
}
```

### Other IDEs

For any MCP-compatible tool, use:

```json
{
  "command": "wellarch-mcp",
  "args": ["start-server"],
  "env": {
    "AWS_PROFILE": "your-profile",
    "AWS_REGION": "your-region"
  }
}
```

## 🚦 Quick Start

### 1. Test Your Connection

```bash
wellarch-mcp test-connection
```

### 2. Start the Server Manually

```bash
wellarch-mcp start-server --host 0.0.0.0 --port 8000
```

### 3. Use with Your AI Assistant

Once configured, you can ask your AI assistant questions like:

- "List my AWS Well-Architected workloads"
- "Show me the lenses available in Well-Architected"
- "Create a new workload for my production environment"
- "What are the improvement recommendations for workload xyz?"
- "Generate a lens review report for my workload"

## 🛠️ Available Tools

The MCP server provides these tools to AI assistants:

| Tool | Description |
|------|-------------|
| `list_lenses` | List available Well-Architected lenses |
| `get_lens_details` | Get detailed information about a specific lens |
| `list_workloads` | List your Well-Architected workloads |
| `get_workload_details` | Get detailed workload information |
| `create_workload` | Create a new workload |
| `list_answers` | List answers for a workload review |
| `get_answer_details` | Get detailed answer information |
| `list_milestones` | List workload milestones |
| `get_lens_review_report` | Generate a lens review report |
| `list_improvement_summaries` | Get improvement recommendations |

## 🧪 Development and Testing

### Local Development

```bash
# Clone the repository
git clone <repository-url>
cd wellarchitected-mcp-server

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy .
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_PROFILE` | AWS profile to use | `default` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `FASTMCP_LOG_LEVEL` | Logging level | `INFO` |

## 📝 Example Usage

Here are some example interactions you can have with your AI assistant:

### List Workloads
> "Show me all my Well-Architected workloads"

### Create a Workload
> "Create a new Well-Architected workload called 'MyApp Production' for a production environment in us-east-1 and us-west-2"

### Get Improvement Recommendations
> "What improvements are recommended for workload abc123?"

### Generate Report
> "Generate a lens review report for my workload xyz789"

## 🔒 Security Considerations

- Always use IAM roles with least-privilege access
- Never hardcode AWS credentials
- Use AWS profiles for different environments
- Monitor MCP server logs for security events
- Keep the server updated to the latest version

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- 📚 Check the [AWS Well-Architected documentation](https://docs.aws.amazon.com/wellarchitected/)
- 🐛 Report issues on GitHub
- 💬 Join our community discussions

## 🚀 What's Next?

- Integration with more AI assistants
- Enhanced reporting capabilities
- Multi-account support
- Custom lens support
- Automated workload analysis

---

Made with ❤️ for the AWS and AI community
