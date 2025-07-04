// UploadCard component for Storybook
export default {
  title: 'Components/UploadCard',
  parameters: {
    docs: {
      description: {
        component: 'A drag-and-drop upload card component for image uploads with preview functionality.'
      }
    }
  },
  argTypes: {
    theme: {
      control: { type: 'select' },
      options: ['light', 'dark'],
      description: 'Visual theme of the component'
    },
    maxFileSize: {
      control: { type: 'number' },
      description: 'Maximum file size in MB'
    },
    acceptedFormats: {
      control: { type: 'object' },
      description: 'Array of accepted file formats'
    },
    showPreview: {
      control: { type: 'boolean' },
      description: 'Whether to show file preview'
    },
    disabled: {
      control: { type: 'boolean' },
      description: 'Disable the upload functionality'
    },
    onFileSelect: {
      action: 'fileSelected',
      description: 'Callback when files are selected'
    },
    onUpload: {
      action: 'uploadStarted',
      description: 'Callback when upload starts'
    }
  }
};

const createUploadCard = ({
  theme = 'dark',
  maxFileSize = 20,
  acceptedFormats = ['JPG', 'PNG', 'GIF', 'WEBP'],
  showPreview = true,
  disabled = false,
  onFileSelect,
  onUpload
}) => {
  const container = document.createElement('div');
  container.className = 'upload-container mb-4';
  container.setAttribute('data-theme', theme);
  
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
      }
      
      [data-theme="light"] {
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --surface-color: #ffffff;
        --text-primary: #333333;
        --text-secondary: #666666;
        --border-color: #e0e0e0;
        --accent-color: #3b82f6;
      }
      
      .upload-card {
        background: var(--surface-color);
        border: 2px dashed var(--border-color);
        border-radius: 16px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        min-height: 300px;
      }
      
      .upload-card:hover:not(.disabled) {
        border-color: var(--accent-color);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
      }
      
      .upload-card.disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
      
      .upload-content {
        padding: 40px 20px;
        text-align: center;
        cursor: pointer;
      }
      
      .upload-content.disabled {
        cursor: not-allowed;
      }
      
      .upload-icon-container {
        margin-bottom: 20px;
      }
      
      .upload-icon {
        font-size: 3rem;
        color: var(--accent-color);
        animation: pulse 2s infinite;
      }
      
      .upload-title {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 10px;
      }
      
      .upload-subtitle {
        color: var(--text-secondary);
        margin-bottom: 20px;
      }
      
      .format-badges {
        display: flex;
        justify-content: center;
        gap: 8px;
        flex-wrap: wrap;
      }
      
      .badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
      }
      
      .badge.bg-light {
        background-color: var(--bg-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
      }
      
      .badge.bg-primary {
        background-color: var(--accent-color);
        color: white;
      }
      
      .upload-limit {
        margin-top: 15px;
        color: var(--text-secondary);
        font-size: 0.9rem;
      }
      
      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
      }
      
      .preview-content {
        padding: 20px;
        display: none;
      }
      
      .preview-title {
        color: var(--text-primary);
        margin-bottom: 15px;
      }
      
      .preview-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
        gap: 10px;
        margin-bottom: 20px;
      }
      
      .preview-item {
        aspect-ratio: 1;
        background: var(--bg-secondary);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-secondary);
        border: 1px solid var(--border-color);
      }
      
      .preview-actions {
        display: flex;
        gap: 10px;
        justify-content: center;
      }
      
      .btn {
        padding: 8px 16px;
        border-radius: 6px;
        border: none;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 5px;
      }
      
      .btn-outline-secondary {
        background: transparent;
        color: var(--text-secondary);
        border: 1px solid var(--border-color);
      }
      
      .btn-outline-secondary:hover {
        background: var(--bg-secondary);
      }
      
      .btn-gradient {
        background: linear-gradient(135deg, var(--accent-color), #2563eb);
        color: white;
      }
      
      .btn-gradient:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
      }
    </style>
  `;
  
  container.innerHTML = styles + `
    <div class="col-md-8 col-lg-6 mx-auto">
      <div class="upload-card ${disabled ? 'disabled' : ''}" id="uploadCard">
        <div class="upload-content ${disabled ? 'disabled' : ''}" id="uploadContent">
          <div class="upload-icon-container">
            <i class="fas fa-cloud-upload-alt upload-icon"></i>
          </div>
          <h4 class="upload-title">Upload Your Images</h4>
          <p class="upload-subtitle">Drag files here or click to select</p>
          <input type="file" multiple accept=".jpg,.jpeg,.png,.gif,.webp" style="display: none;" id="fileInput" ${disabled ? 'disabled' : ''}>
          <div class="upload-formats mt-3">
            <p class="upload-hint mb-2">Supported formats:</p>
            <div class="format-badges">
              ${acceptedFormats.map(format => `<span class="badge bg-light">${format}</span>`).join('')}
            </div>
            <p class="upload-limit mt-2">Max size: <span class="badge bg-primary">${maxFileSize}MB</span></p>
          </div>
        </div>
        
        ${showPreview ? `
        <div class="preview-content" id="previewContent">
          <h5 class="preview-title">Preview</h5>
          <div class="preview-grid" id="previewGrid">
            <div class="preview-item">
              <i class="fas fa-image"></i>
            </div>
            <div class="preview-item">
              <i class="fas fa-image"></i>
            </div>
          </div>
          <div class="preview-actions">
            <button class="btn btn-outline-secondary" id="cancelBtn">
              <i class="fas fa-times"></i> Cancel
            </button>
            <button class="btn btn-gradient" id="uploadBtn">
              <i class="fas fa-upload"></i> Upload (2)
            </button>
          </div>
        </div>
        ` : ''}
      </div>
    </div>
  `;
  
  // Add event listeners
  if (!disabled) {
    const uploadContent = container.querySelector('#uploadContent');
    const fileInput = container.querySelector('#fileInput');
    const previewContent = container.querySelector('#previewContent');
    const cancelBtn = container.querySelector('#cancelBtn');
    const uploadBtn = container.querySelector('#uploadBtn');
    
    uploadContent.addEventListener('click', () => {
      fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        onFileSelect?.(e.target.files);
        if (showPreview && previewContent) {
          uploadContent.style.display = 'none';
          previewContent.style.display = 'block';
        }
      }
    });
    
    cancelBtn?.addEventListener('click', () => {
      if (previewContent) {
        previewContent.style.display = 'none';
        uploadContent.style.display = 'block';
      }
      fileInput.value = '';
    });
    
    uploadBtn?.addEventListener('click', () => {
      onUpload?.(fileInput.files);
    });
  }
  
  return container;
};

export const Default = {
  render: (args) => createUploadCard(args),
  args: {
    theme: 'dark',
    maxFileSize: 20,
    acceptedFormats: ['JPG', 'PNG', 'GIF', 'WEBP'],
    showPreview: true,
    disabled: false
  }
};

export const LightTheme = {
  render: (args) => createUploadCard(args),
  args: {
    theme: 'light',
    maxFileSize: 20,
    acceptedFormats: ['JPG', 'PNG', 'GIF', 'WEBP'],
    showPreview: true,
    disabled: false
  }
};

export const WithoutPreview = {
  render: (args) => createUploadCard(args),
  args: {
    theme: 'dark',
    maxFileSize: 10,
    acceptedFormats: ['JPG', 'PNG'],
    showPreview: false,
    disabled: false
  }
};

export const Disabled = {
  render: (args) => createUploadCard(args),
  args: {
    theme: 'dark',
    maxFileSize: 20,
    acceptedFormats: ['JPG', 'PNG', 'GIF', 'WEBP'],
    showPreview: true,
    disabled: true
  }
};
