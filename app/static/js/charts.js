// Função para criar gráfico de vendas do barbeiro
function createBarberChart(chartId, data) {
    const ctx = document.getElementById(chartId).getContext('2d');
    
    // Extrair dados do array
    const labels = data.map(item => item.data);
    const values = data.map(item => item.valor);
    
    // Definir as cores do tema camuflado brasileiro
    const camoGreenDark = '#225522';
    const camoGreenMedium = '#557755';
    const camoGreenLight = '#889988';
    const camoBrown = '#77553f';
    const camoSand = '#bdb76b';
    
    // Criar gradiente para barras
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, camoGreenDark);
    gradient.addColorStop(1, camoGreenLight);
    
    // Criar o gráfico
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Valor (R$)',
                data: values,
                backgroundColor: gradient,
                borderColor: camoGreenDark,
                borderWidth: 1,
                borderRadius: 5,
                barPercentage: 0.6,
                categoryPercentage: 0.8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `R$ ${context.raw.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value;
                        },
                        font: {
                            size: 12
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
    
    return chart;
}

// Função para criar gráfico de distribuição de agendamentos por dia da semana (Admin)
function createAdminAgendamentosChart(chartId, data) {
    const ctx = document.getElementById(chartId).getContext('2d');
    
    // Definir as cores do tema camuflado brasileiro
    const camoGreenDark = '#225522';
    const camoGreenMedium = '#557755';
    const camoGreenLight = '#889988';
    const camoBrown = '#77553f';
    const camoSand = '#bdb76b';
    
    // Cores para o gráfico
    const backgroundColors = [
        camoGreenDark,
        camoGreenMedium,
        camoGreenLight,
        camoBrown,
        camoSand,
        '#3d6a3d',
        '#6a8e6a'
    ];
    
    // Criar o gráfico
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: backgroundColors,
                borderColor: '#ffffff',
                borderWidth: 2,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            size: 12
                        },
                        padding: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${context.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '60%',
            radius: '90%'
        }
    });
    
    return chart;
}

// Função para criar gráfico de vendas por barbeiro (Admin)
function createAdminVendasChart(chartId, data) {
    const ctx = document.getElementById(chartId).getContext('2d');
    
    // Extrair dados
    const labels = data.map(item => item.barbeiro);
    const values = data.map(item => item.valor);
    
    // Definir as cores do tema camuflado brasileiro
    const camoGreenDark = '#225522';
    const camoGreenMedium = '#557755';
    const camoGreenLight = '#889988';
    
    // Criar o gráfico
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Valor Total (R$)',
                data: values,
                backgroundColor: camoGreenMedium,
                borderColor: camoGreenDark,
                borderWidth: 1,
                borderRadius: 5,
                barPercentage: 0.7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `R$ ${context.raw.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value;
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
    
    return chart;
}
