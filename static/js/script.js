// Poll for QR code data
function startQRDataPolling() {
    const statusIndicator = document.getElementById('status-indicator');
    const qrDataInput = document.getElementById('qr_data');
    const submitBtn = document.getElementById('submitBtn');
    
    // Poll every 500ms
    const pollingInterval = setInterval(() => {
        fetch('/check_qr_data')
            .then(response => response.json())
            .then(data => {
                if (data.detected) {
                    // QR code detected
                    statusIndicator.textContent = 'QR Code Detected!';
                    statusIndicator.className = 'detected';
                    
                    // Fill in the form
                    qrDataInput.value = data.data;
                    
                    // Enable the submit button
                    submitBtn.disabled = false;
                    
                    // Auto-submit after a short delay
                    setTimeout(() => {
                        document.getElementById('qrForm').submit();
                    }, 1000); 
                    
                    // Stop polling
                    clearInterval(pollingInterval);
                }
            })
            .catch(error => {
                console.error('Error polling for QR data:', error);
            });
    }, 500);
}