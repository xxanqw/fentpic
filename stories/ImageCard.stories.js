// ImageCard component for Storybook
export default {
  title: 'Components/ImageCard',
  parameters: {
    docs: {
      description: {
        component: 'A card component for displaying uploaded images with metadata and action buttons.'
      }
    }
  },
  argTypes: {
    image: {
      control: { type: 'object' },
      description: 'Image object with metadata'
    },
    theme: {
      control: { type: 'select' },
      options: ['light', 'dark'],
      description: 'Visual theme of the component'
    },
    showActions: {
      control: { type: 'boolean' },
      description: 'Whether to show action buttons'
    },
    showMetadata: {
      control: { type: 'boolean' },
      description: 'Whether to show image metadata'
    },
    size: {
      control: { type: 'select' },
      options: ['small', 'medium', 'large'],
      description: 'Size variant of the card'
    },
    onCopy: {
      action: 'copyClicked',
      description: 'Callback when copy button is clicked'
    },
    onDelete: {
      action: 'deleteClicked',
      description: 'Callback when delete button is clicked'
    },
    onView: {
      action: 'viewClicked',
      description: 'Callback when view button is clicked'
    }
  }
};

const createImageCard = ({
  image = {
    id: 1,
    filename: 'sample-image.jpg',
    url: 'https://via.placeholder.com/300x200/3b82f6/ffffff?text=Sample+Image',
    size: 1048576,
    uploaded_at: '2025-07-04T12:00:00Z',
    is_public: true
  },
  theme = 'dark',
  showActions = true,
  showMetadata = true,
  size = 'medium',
  onCopy,
  onDelete,
  onView
}) => {
  const container = document.createElement('div');
  container.className = `image-card-container ${size}`;
  container.setAttribute('data-theme', theme);
  
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  const styles = `
    <style>
      [data-theme="dark"] {
        --bg-primary: #0f0f0f;
        --bg-secondary: #1a1a1a;
        --surface-color: #262626;
        --text-primary: #ffffff;
        --text-secondary: #b3b3b3;
        --border-color: #404040;
        --accent-color: #3b82f6;
        --success-color: #10b981;
        --danger-color: #ef4444;
      }
      
      [data-theme="light"] {
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --surface-color: #ffffff;
        --text-primary: #333333;
        --text-secondary: #666666;
        --border-color: #e0e0e0;
        --accent-color: #3b82f6;
        --success-color: #10b981;
        --danger-color: #ef4444;
      }
      
      .image-card {
        background: var(--surface-color);
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        position: relative;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
      
      .image-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border-color: var(--accent-color);
      }
      
      .image-card.small {
        max-width: 200px;
      }
      
      .image-card.medium {
        max-width: 300px;
      }
      
      .image-card.large {
        max-width: 400px;
      }
      
      .image-preview {
        position: relative;
        aspect-ratio: 16/10;
        overflow: hidden;
        background: var(--bg-secondary);
      }
      
      .image-preview img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
      }
      
      .image-card:hover .image-preview img {
        transform: scale(1.05);
      }
      
      .privacy-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
        backdrop-filter: blur(10px);
      }
      
      .privacy-badge.public {
        background: rgba(16, 185, 129, 0.9);
        color: white;
      }
      
      .privacy-badge.private {
        background: rgba(239, 68, 68, 0.9);
        color: white;
      }
      
      .image-info {
        padding: 16px;
      }
      
      .image-title {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 8px;
        word-break: break-word;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
      
      .image-metadata {
        display: flex;
        flex-direction: column;
        gap: 4px;
        margin-bottom: 12px;
      }
      
      .metadata-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: var(--text-secondary);
        font-size: 0.85rem;
      }
      
      .metadata-label {
        font-weight: 500;
      }
      
      .image-actions {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
      
      .btn {
        padding: 6px 12px;
        border-radius: 6px;
        border: none;
        cursor: pointer;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        flex: 1;
        justify-content: center;
        min-width: 70px;
      }
      
      .btn-outline-primary {
        background: transparent;
        color: var(--accent-color);
        border: 1px solid var(--accent-color);
      }
      
      .btn-outline-primary:hover {
        background: var(--accent-color);
        color: white;
      }
      
      .btn-outline-success {
        background: transparent;
        color: var(--success-color);
        border: 1px solid var(--success-color);
      }
      
      .btn-outline-success:hover {
        background: var(--success-color);
        color: white;
      }
      
      .btn-outline-danger {
        background: transparent;
        color: var(--danger-color);
        border: 1px solid var(--danger-color);
      }
      
      .btn-outline-danger:hover {
        background: var(--danger-color);
        color: white;
      }
      
      .loading-placeholder {
        background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--border-color) 50%, var(--bg-secondary) 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
      }
      
      @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
      }
    </style>
  `;
  
  container.innerHTML = styles + `
    <div class="image-card">
      <div class="image-preview">
        <img src="${image.url}" alt="${image.filename}" loading="lazy" />
        <div class="privacy-badge ${image.is_public ? 'public' : 'private'}">
          <i class="fas ${image.is_public ? 'fa-globe' : 'fa-lock'}"></i>
          ${image.is_public ? 'Public' : 'Private'}
        </div>
      </div>
      <div class="image-info">
        <h6 class="image-title">${image.filename}</h6>
        ${showMetadata ? `
        <div class="image-metadata">
          <div class="metadata-item">
            <span class="metadata-label">Size:</span>
            <span>${formatFileSize(image.size)}</span>
          </div>
          <div class="metadata-item">
            <span class="metadata-label">Uploaded:</span>
            <span>${formatDate(image.uploaded_at)}</span>
          </div>
          <div class="metadata-item">
            <span class="metadata-label">ID:</span>
            <span>#${image.id}</span>
          </div>
        </div>
        ` : ''}
        ${showActions ? `
        <div class="image-actions">
          <button class="btn btn-outline-primary" id="viewBtn">
            <i class="fas fa-eye"></i>
            <span>View</span>
          </button>
          <button class="btn btn-outline-success" id="copyBtn">
            <i class="fas fa-copy"></i>
            <span>Copy</span>
          </button>
          <button class="btn btn-outline-danger" id="deleteBtn">
            <i class="fas fa-trash"></i>
            <span>Delete</span>
          </button>
        </div>
        ` : ''}
      </div>
    </div>
  `;
  
  // Add event listeners
  if (showActions) {
    const viewBtn = container.querySelector('#viewBtn');
    const copyBtn = container.querySelector('#copyBtn');
    const deleteBtn = container.querySelector('#deleteBtn');
    
    viewBtn?.addEventListener('click', () => onView?.(image));
    copyBtn?.addEventListener('click', () => onCopy?.(image));
    deleteBtn?.addEventListener('click', () => onDelete?.(image));
  }
  
  return container;
};

export const Default = {
  render: (args) => createImageCard(args),
  args: {
    theme: 'dark',
    showActions: true,
    showMetadata: true,
    size: 'medium'
  }
};

export const LightTheme = {
  render: (args) => createImageCard(args),
  args: {
    theme: 'light',
    showActions: true,
    showMetadata: true,
    size: 'medium'
  }
};

export const PrivateImage = {
  render: (args) => createImageCard(args),
  args: {
    image: {
      id: 2,
      filename: 'private-document.png',
      url: 'https://via.placeholder.com/300x200/ef4444/ffffff?text=Private+Image',
      size: 2097152,
      uploaded_at: '2025-07-04T10:30:00Z',
      is_public: false
    },
    theme: 'dark',
    showActions: true,
    showMetadata: true,
    size: 'medium'
  }
};

export const SmallSize = {
  render: (args) => createImageCard(args),
  args: {
    theme: 'dark',
    showActions: true,
    showMetadata: true,
    size: 'small'
  }
};

export const LargeSize = {
  render: (args) => createImageCard(args),
  args: {
    theme: 'dark',
    showActions: true,
    showMetadata: true,
    size: 'large'
  }
};

export const WithoutActions = {
  render: (args) => createImageCard(args),
  args: {
    theme: 'dark',
    showActions: false,
    showMetadata: true,
    size: 'medium'
  }
};

export const WithoutMetadata = {
  render: (args) => createImageCard(args),
  args: {
    theme: 'dark',
    showActions: true,
    showMetadata: false,
    size: 'medium'
  }
};
