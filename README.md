# QueueChain - Decentralized Music Streaming Platform

⚖️ On-chain Auction Queueing: Dynamic Priority Bidding through Smart Contracts for Real-Time Resource Allocation 
(to queue up songs, videos, and memes!)

QueueChain replaces inefficient FIFO (First-in First-out) playlists with **demand-sensitive bidding**. Users bid ETH to prioritize their content, allowing urgent users to express preference intensity through willingness-to-pay. The smart contract maintains an ordered list of URLs indexed by transaction value, automatically reordering submissions so higher bidders move up the rank.

This fixes FIFO's deadweight loss in scarce resource allocation and better captures consumer utilities compared to traditional optimization strategies. The model can be applied to business resource management like passenger boarding or patient waiting lists - anywhere demand-sensitivity improves allocation efficiency.

## 🎵 Live Demo & Resources

- **🎬 Video Demo**: [Watch on YouTube](https://youtu.be/Zn2tbIU-FBU)
- **🌐 Live dApp**: [q-chain-fwb5aegndpdug7bu.uksouth-01.azurewebsites.net](http://q-chain-fwb5aegndpdug7bu.uksouth-01.azurewebsites.net)
- **📄 Smart Contract**: [View on Polygon zkEVM Explorer](https://cardona-zkevm.polygonscan.com/address/0x1a7dbe663e5efb9f3aaf2eb56616794069d3f4ea)

## 🚀 Features

- **Decentralized Queue System**: Users bid with ETH to prioritize their content
- **Automatic Progression**: Smart contract advances queue every 3 minutes
- **YouTube Integration**: Automatic conversion of YouTube URLs to embedded players with autoplay
- **Real-time Updates**: Live queue statistics and metadata display
- **Responsive Design**: Spotify-inspired UI with glassmorphism effects
- **Secure Wallet Integration**: In-memory private key management
- **Background Services**: Automated queue management and content monitoring

## 🛠 Technology Stack

- **Backend**: FastAPI (Python 3.8+) with async/await patterns
- **Blockchain**: Web3.py for Ethereum smart contract interaction
- **Network**: Polygon zkEVM testnet (Cardona)
- **Frontend**: Vanilla JavaScript with modern CSS3
- **Design**: Spotify-inspired dark theme with glassmorphism effects

## 📂 Project Structure

```
QueueChain/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration constants (RPC URL, Contract Address)
├── contract.abi           # Smart contract ABI definition
├── requirements.txt       # Python dependencies
├── startup.sh            # Deployment script
├── templates/
│   └── index.html         # Single-page application frontend
├── docs/
│   ├── DEVELOPMENT_GUIDE.md
│   └── COMPREHENSIVE_DOCUMENTATION.md
├── CLAUDE.md              # Claude development context
├── CLAUDE_CODE_PROMPT.md  # Complete prompt for AI code generation
└── README.md              # This file
```

## 🏃‍♂️ Quick Start

### Prerequisites
- Python 3.8+
- Ethereum wallet with private key
- Some testnet ETH on Polygon zkEVM Cardona network

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd QueueChain
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   Open your browser and go to `http://localhost:8000`

### Usage

1. **Connect Wallet**: Enter your private key in the sidebar (stored in memory only)
2. **Submit Content**: Add a music URL (YouTube supported) and bid amount in Wei
3. **Watch Queue**: View live queue statistics and upcoming content
4. **Enjoy**: Content plays automatically and advances every 3 minutes

## 🔧 Configuration

### Environment Variables
- `RPC_URL`: Polygon zkEVM RPC endpoint (default: Cardona testnet)
- `CONTRACT_ADDRESS`: Smart contract address on Polygon zkEVM

### Smart Contract Configuration
- **Network**: Polygon zkEVM Cardona Testnet
- **Contract Address**: `0x1a7dbe663E5efb9f3aAF2EB56616794069d3F4eA`
- **RPC URL**: `https://rpc.cardona.zkevm-rpc.com`

## 🤖 AI Development Resources

This project includes comprehensive documentation for AI-assisted development and replication:

### For Claude AI Development

📁 **Claude Development Files**:

- **`CLAUDE_CODE_PROMPT.md`** (Root directory) - Complete prompt for generating the entire QueueChain service from scratch
  - Detailed technical specifications
  - Step-by-step implementation instructions
  - Security requirements and patterns
  - Testing checklist and success criteria

- **`CLAUDE.md`** (Root directory) - Quick context file for project understanding
  - Essential project overview
  - Key implementation patterns
  - Security considerations

📁 **Documentation Directory** (`/docs/`):

- **`COMPREHENSIVE_DOCUMENTATION.md`** - In-depth technical documentation
  - Server architecture details
  - FastAPI endpoint specifications
  - Web3 blockchain integration patterns
  - CSS styling system documentation

- **`DEVELOPMENT_GUIDE.md`** - Developer-focused implementation guide
  - Component documentation
  - Development patterns
  - API endpoint details

### How to Use AI Development Files

1. **For Complete Code Generation**: 
   ```
   Use: CLAUDE_CODE_PROMPT.md
   Purpose: Generate entire project from scratch with one prompt
   ```

2. **For Quick Understanding**: 
   ```
   Use: CLAUDE.md
   Purpose: Rapid project comprehension and context
   ```

3. **For Deep Technical Dive**: 
   ```
   Use: docs/COMPREHENSIVE_DOCUMENTATION.md
   Purpose: Detailed technical specifications and patterns
   ```

4. **For Development Guidelines**: 
   ```
   Use: docs/DEVELOPMENT_GUIDE.md
   Purpose: Implementation patterns and best practices
   ```

These files are specifically designed to enable AI agents to understand, replicate, and extend the QueueChain platform with minimal human intervention.

## 🔒 Security Features

- **Private Key Safety**: Private keys stored only in memory, never persisted
- **Input Validation**: Comprehensive validation of all user inputs
- **Error Handling**: Graceful handling of blockchain and network errors
- **Transaction Security**: Proper gas estimation and transaction signing

## 🌐 Blockchain Integration

### Smart Contract Functions
- `getCurrentSong()` - Get currently playing content
- `submitData(string)` - Submit content with ETH bid (payable)
- `popIfReady()` - Advance queue (3-minute cooldown)
- `getSubmissionCount()` - Get total queue items
- `getSubmissionByIndex(uint256)` - Get submission details by index

### Background Services
- **Queue Advancement**: Automatically calls `popIfReady()` every 3 minutes
- **Content Monitoring**: Monitors current song every 3.05 minutes for logging

## 🎨 Frontend Features

- **Responsive Design**: Mobile-first design that works on all devices
- **Queue Dropdown**: Hover-triggered dropdown with live queue information
- **YouTube Integration**: Automatic conversion of YouTube URLs to embedded players with autoplay
- **Autoplay Support**: Media content starts automatically when queue advances
- **Real-time Updates**: Auto-refresh every 60 seconds
- **Status Messages**: Loading, error, and success states
- **Glassmorphism UI**: Modern glass-effect styling with smooth animations

## 🚀 Deployment

### Development
```bash
python main.py
```
Application runs on `http://localhost:8000`

### Production
The application is deployed on Azure Web Apps:
- **Live URL**: [q-chain-fwb5aegndpdug7bu.uksouth-01.azurewebsites.net](http://q-chain-fwb5aegndpdug7bu.uksouth-01.azurewebsites.net)
- **Configuration**: Single worker for state consistency
- **Background Services**: Daemon threads for queue management

## 🧪 Testing

### Backend Testing
- Blockchain connection validation
- Private key format validation
- API endpoint functionality
- Background service operation

### Frontend Testing
- Private key input validation
- Form submission handling
- Auto-refresh functionality
- Responsive design verification

## 📚 API Documentation

### Endpoints

- `GET /` - Serve frontend application
- `GET /current-url` - Get currently playing content URL
- `GET /queue-metadata` - Get comprehensive queue information
- `GET /account-info` - Get wallet connection status
- `POST /submit-bid` - Submit content with ETH bid
- `POST /update-private-key` - Store private key and create account

### Response Formats
All API endpoints return JSON with consistent error handling:
```json
{
  "success": true,
  "data": { ... }
}
```
or
```json
{
  "error": "Error message"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code patterns and security practices
- Ensure private keys are never persisted
- Test all blockchain interactions thoroughly
- Maintain responsive design principles
- Update documentation for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Polygon zkEVM for providing the blockchain infrastructure
- FastAPI for the excellent web framework
- Web3.py for seamless blockchain integration
- Font Awesome for the icon library

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Documentation**: Check the `/docs/` directory for comprehensive guides
- **Video Demo**: [Watch the demo](https://youtu.be/Zn2tbIU-FBU) for usage examples
- **Live App**: [Try the live version](http://q-chain-fwb5aegndpdug7bu.uksouth-01.azurewebsites.net)

---

**Built with ❤️ for the decentralized web**