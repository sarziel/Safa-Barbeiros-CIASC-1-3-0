// Função para preview de imagem
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    const file = input.files[0];
    
    if (file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        
        reader.readAsDataURL(file);
    } else {
        preview.src = '';
        preview.style.display = 'none';
    }
}

// Inicializar preview de imagem quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Para a foto de perfil
    const fotoInput = document.getElementById('foto');
    if (fotoInput) {
        fotoInput.addEventListener('change', function() {
            previewImage(this, 'foto-preview');
        });
    }
    
    // Verifica se há erros de validação e mantém preview se necessário
    const fotoPreview = document.getElementById('foto-preview');
    if (fotoPreview && fotoPreview.getAttribute('src') && fotoPreview.getAttribute('src') !== '') {
        fotoPreview.style.display = 'block';
    }
    
    // Validação de tamanho e formato de arquivo
    const fotoUploadForm = document.querySelector('form');
    if (fotoUploadForm && fotoInput) {
        fotoUploadForm.addEventListener('submit', function(event) {
            if (fotoInput.files.length > 0) {
                const file = fotoInput.files[0];
                const fileSize = file.size / 1024 / 1024; // em MB
                const allowedFormats = ['image/jpeg', 'image/png', 'image/jpg'];
                
                // Verifica tamanho do arquivo (máximo 5MB)
                if (fileSize > 5) {
                    event.preventDefault();
                    alert('O tamanho do arquivo não deve exceder 5MB.');
                    return false;
                }
                
                // Verifica formato do arquivo
                if (!allowedFormats.includes(file.type)) {
                    event.preventDefault();
                    alert('Formato de arquivo inválido. Use apenas JPEG, JPG ou PNG.');
                    return false;
                }
            }
            
            return true;
        });
    }
    
    // Drag and drop para upload
    const dropArea = document.getElementById('drop-area');
    if (dropArea && fotoInput) {
        // Prevenir comportamento padrão de arrastar e soltar
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Estilo visual para quando arrastar sobre a área
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropArea.classList.add('highlight');
        }
        
        function unhighlight() {
            dropArea.classList.remove('highlight');
        }
        
        // Lidar com o arquivo solto
        dropArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            fotoInput.files = files;
            
            // Mostrar preview
            previewImage(fotoInput, 'foto-preview');
        }
    }
});
