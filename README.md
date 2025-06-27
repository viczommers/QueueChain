# Encode Play
⚖️ On-chain Auction Queueing: Dynamic Priority Bidding through Smart Contracts for Real-Time Resource Allocation (to queue up songs, videos, and memes!)

Encode Play replaces inefficient FIFO (First-in First-out) Playlists with **demand-sensitive bidding**. Users bid ETH to prioritize their content (music), allowing urgent users to express preference intensity through willingness-to-pay. The smart contract maintains an ordered list of URLs indexed by transaction (donation) value, automatically reordering submissions so higher bidders move up the rank.

This fixes FIFO's deadweight loss in scarce resource allocation and better captures consumer utilities compared to traditional optimization strategies. The model can be applied to business resource management like **passenger boarding**, **ticket sales** and **patient waiting lists** - anywhere demand-sensitivity improves allocation efficiency.

## 🎵 Live Demo & Resources

- **🎬 Video Demo**: [Watch on YouTube](https://youtu.be/Zn2tbIU-FBU)
- **🌐 Live dApp**: [viczommers.github.io/encode-play/](https://viczommers.github.io/encode-play/)
- **📄 Smart Contract**: [View on Polygon zkEVM Explorer](https://cardona-zkevm.polygonscan.com/address/0x1a7dbe663e5efb9f3aaf2eb56616794069d3f4ea)
- **TestNet Tokens Faucet**: [Polygon zkEVM Cardona Faucet](https://faucet.triangleplatform.com/polygonzkevm/cardona)

## 🚀 Features

- **Decentralized Queue System**: Users bid with ETH to prioritize their content
- **Automatic Progression**: Smart contract advances queue every 3 minutes via client-side calls
- **YouTube Integration**: Automatic conversion of YouTube URLs to embedded players with autoplay (unmuted)
- **Real-time Updates**: Live queue statistics and metadata display
- **Responsive Design**: Glassmorphism UI with disco-inspired elements and electric blue accents
- **Secure Wallet Integration**: Browser memory-only private key management
- **Static Deployment**: Single HTML file works on any static hosting platform

## 🛠 Technology Stack

- **Architecture**: Single static HTML file with embedded CSS and JavaScript
- **Blockchain**: Web3.js for direct Ethereum smart contract interaction
- **Network**: Polygon zkEVM testnet (Cardona)
- **Frontend**: Vanilla JavaScript with modern CSS3
- **Design**: Glassmorphism dark theme with disco-inspired elements, electric blue accents, and shimmer animations
- **Deployment**: Static hosting (GitHub Pages, Netlify, Vercel, etc.)

## 📂 Project Structure

```
QueueChain/
├── index.html              # Complete static application (all-in-one file)
├── static/
│   └── logo.png            # Logo image (optional)
├── docs/
│   ├── DEVELOPMENT_GUIDE.md
│   └── COMPREHENSIVE_DOCUMENTATION.md
├── CLAUDE.md              # Claude development context
├── CLAUDE_CODE_PROMPT.md  # Complete prompt for AI code generation
└── README.md              # This file
```

## 🏃‍♂️ Quick Start

### Prerequisites
- Modern web browser with JavaScript enabled
- Ethereum wallet with private key
- Some testnet ETH on Polygon zkEVM Cardona network

### Installation

1. **Download the file**
   ```bash
   git clone <repository-url>
   cd QueueChain
   ```

2. **Open in browser**
   - Simply open `index.html` in your web browser
   - Or deploy to any static hosting service

3. **Access the application**
   - Local: Open `index.html` directly in browser
   - Hosted: Visit your deployed URL

### Usage

1. **Connect Wallet**: Enter your private key in the sidebar (stored in browser memory only)
2. **Submit Content**: Add a music URL (YouTube supported) and bid amount in Wei
3. **Watch Queue**: View live queue statistics and upcoming content with real YouTube titles
4. **Enjoy**: Content plays automatically with unmuted audio and advances every 3 minutes

## 🌐 Deployment Options

### Static Hosting Platforms

**GitHub Pages**:
```bash
# Push to gh-pages branch
git checkout -b gh-pages
git add index.html static/
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages
```

**Netlify**:
- Drag and drop the project folder to Netlify dashboard
- Or connect your GitHub repository

**Vercel**:
- Connect your GitHub repository to Vercel
- Automatic deployment on push

**Surge**:
```bash
npm install -g surge
surge ./
```

**Any Web Server**:
- Upload `index.html` and `static/` folder to your web server
- No server-side processing required

## 🔧 Configuration

### Smart Contract Configuration
- **Network**: Polygon zkEVM Cardona Testnet
- **Contract Address**: `0x1a7dbe663E5efb9f3aAF2EB56616794069d3F4eA`
- **RPC URL**: `https://rpc.cardona.zkevm-rpc.com`

All configuration is embedded in the HTML file - no external config files needed.

## 🤖 AI Development Resources

This project includes comprehensive documentation for AI-assisted development and replication:

### For Claude AI Development

📁 **Claude Development Files**:

- **`CLAUDE_CODE_PROMPT.md`** (Root directory) - Complete prompt for generating the entire static QueueChain application
  - Single HTML file specifications
  - Client-side Web3.js integration patterns
  - Security requirements for browser-only implementation
  - Static hosting deployment instructions
  - Testing checklist and success criteria

- **`CLAUDE.md`** (Root directory) - Quick context file for static implementation
  - Essential project overview for single-file architecture
  - Key client-side implementation patterns
  - Browser security considerations

📁 **Documentation Directory** (`/docs/`):

- **`COMPREHENSIVE_DOCUMENTATION.md`** - In-depth technical documentation
  - Static architecture details
  - Web3.js blockchain integration patterns
  - Embedded CSS styling system documentation

- **`DEVELOPMENT_GUIDE.md`** - Developer-focused implementation guide
  - Component documentation for static implementation
  - Client-side development patterns
  - Browser-based functionality details

### How to Use AI Development Files

1. **For Complete Code Generation**: 
   ```
   Use: CLAUDE_CODE_PROMPT.md
   Purpose: Generate entire static HTML application from scratch
   ```

2. **For Quick Understanding**: 
   ```
   Use: CLAUDE.md
   Purpose: Rapid project comprehension for static architecture
   ```

3. **For Deep Technical Dive**: 
   ```
   Use: docs/COMPREHENSIVE_DOCUMENTATION.md
   Purpose: Detailed technical specifications for client-side patterns
   ```

4. **For Development Guidelines**: 
   ```
   Use: docs/DEVELOPMENT_GUIDE.md
   Purpose: Implementation patterns for static deployment
   ```

These files are specifically designed to enable AI agents to understand, replicate, and extend the QueueChain platform as a static decentralized application.

## 🔒 Security Features

- **Private Key Safety**: Private keys stored only in browser memory, never persisted to disk or localStorage
- **Client-Side Only**: No server-side processing or storage
- **Input Validation**: Comprehensive validation of all user inputs before blockchain operations
- **Error Handling**: Graceful handling of blockchain and network errors
- **Transaction Security**: Proper gas estimation and transaction signing via Web3.js

## 🌐 Blockchain Integration

### Smart Contract Functions
- `getCurrentSong()` - Get currently playing content
- `submitData(string)` - Submit content with ETH bid (payable)
- `popIfReady()` - Advance queue (3-minute cooldown)
- `getSubmissionCount()` - Get total queue items
- `getSubmissionByIndex(uint256)` - Get submission details by index
- `getSubmitterByIndex(uint256)` - Get submitter address by index
- `getTimestampByIndex(uint256)` - Get submission timestamp by index

### Client-Side Background Services
- **Queue Advancement**: Automatically calls `popIfReady()` every 3 minutes (with empty queue check for efficiency)
- **Content Monitoring**: Real-time content change detection every 5 seconds
- **Metadata Updates**: Queue information refresh every 30 seconds

## 🎨 Frontend Features

- **Responsive Design**: Mobile-first design that works on all devices
- **Queue Dropdown**: Hover-triggered dropdown with live queue information (purple gradient badge)
- **Help Dropdown**: Hover-triggered dropdown explaining bidding system and tips (red gradient badge)
- **Mobile Optimized Dropdowns**: Centered dropdowns with proper positioning on mobile devices
- **YouTube Integration**: Automatic conversion of YouTube URLs to embedded players with autoplay (unmuted)
- **YouTube Title Fetching**: Real video titles fetched via YouTube oEmbed API
- **Autoplay Support**: Media content starts automatically when queue advances
- **Real-time Updates**: Auto-refresh with change detection (5s content, 30s metadata)
- **Status Messages**: Loading, error, and success states with animated loading spinner
- **Glassmorphism UI**: Modern glass-effect styling with shimmer animations

## 🧪 Testing

### Client-Side Testing
- Blockchain connection validation via Web3.js
- Private key format validation (64 hex characters)
- Smart contract interaction functionality
- Real-time update system operation

### Frontend Testing
- Private key input validation
- Form submission handling
- Auto-refresh functionality with change detection
- Responsive design verification
- YouTube title extraction testing
- Loading animation and error state handling

### Browser Compatibility
- Modern browsers with ES6+ support
- Web3.js CDN loading
- Font Awesome icon loading
- YouTube oEmbed API access

## 📚 Application Architecture

### Single-File Structure
The entire application is contained in `index.html` with:
- **Embedded CSS**: Complete glassmorphism design system
- **Embedded JavaScript**: Full Web3 blockchain interaction
- **CDN Dependencies**: Font Awesome icons and Web3.js library
- **Self-contained**: No external files required except optional logo

### Key Functions
- `initBlockchain()` - Initialize Web3 connection
- `setPrivateKey()` - Validate and store private key in memory
- `loadCurrentSong()` - Load and display current content
- `submitBid()` - Submit content bid via smart contract
- `loadQueueMetadata()` - Update queue information
- `extractContentTitle()` - Fetch YouTube video titles
- `checkForUpdates()` - Real-time content change detection
- `popIfReady()` - Client-side queue advancement

### Real-time Updates
- Content change detection every 5 seconds
- Queue metadata refresh every 30 seconds
- Automatic queue advancement every 3 minutes
- YouTube title fetching with graceful fallbacks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Modify the `index.html` file with your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines
- Maintain the single-file architecture
- Ensure all functionality remains client-side only
- Follow existing security practices (no private key persistence)
- Test all blockchain interactions thoroughly
- Maintain responsive design principles
- Update embedded documentation for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Polygon zkEVM for providing the blockchain infrastructure
- Web3.js for seamless client-side blockchain integration
- Font Awesome for the icon library
- YouTube oEmbed API for video title extraction
- Static hosting platforms for free deployment options

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Documentation**: Check the `/docs/` directory for comprehensive guides
- **Video Demo**: [Watch the demo](https://youtu.be/Zn2tbIU-FBU) for usage examples
- **Live App**: [Try the live version](https://viczommers.github.io/encode-play/)

---

**Built with ❤️ for the decentralized web - Now 100% client-side!**