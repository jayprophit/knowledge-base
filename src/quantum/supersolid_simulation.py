"""
Supersolid Light Simulation
--------------------------
This module simulates supersolid light behavior in a 2D exciton-polariton system,
demonstrating the coexistence of crystalline order and superfluidity.

Key Features:
- Real-time visualization of density and phase
- Adjustable system parameters
- Multiple potential landscapes
- Quantum vortex dynamics
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
from scipy.fft import fft2, ifft2, fftshift
from scipy.ndimage import gaussian_filter
from typing import Tuple, Optional

class SupersolidLightSimulator:
    """
    Simulates supersolid light in a 2D exciton-polariton system.
    
    The simulation demonstrates the formation of a supersolid phase through
    the spontaneous breaking of translational symmetry in a polariton condensate.
    """
    
    def __init__(self, size: int = 256, dt: float = 0.05, hbar: float = 1.0, 
                 m: float = 1.0, potential_type: str = 'lattice', 
                 g: float = 1.0, mu: float = 0.0):
        """
        Initialize the supersolid light simulator.
        
        Args:
            size: Number of grid points along each dimension
            dt: Time step for the simulation
            hbar: Reduced Planck constant
            m: Effective mass of polaritons
            potential_type: Type of external potential ('lattice', 'trap', or 'none')
            g: Interaction strength (nonlinearity coefficient)
            mu: Chemical potential
        """
        self.size = size
        self.dt = dt
        self.hbar = hbar
        self.m = m
        self.g = g  # Interaction strength
        self.mu = mu  # Chemical potential
        
        # Spatial grid
        self.L = 10.0  # System size
        x = np.linspace(-self.L/2, self.L/2, size, endpoint=False)
        y = np.linspace(-self.L/2, self.L/2, size, endpoint=False)
        self.X, self.Y = np.meshgrid(x, y)
        
        # Initialize wavefunction with random phase
        np.random.seed(42)  # For reproducibility
        phase = 2 * np.pi * np.random.rand(size, size)
        self.psi = np.exp(1j * phase)
        
        # Set up potential
        self.potential_type = potential_type
        self.V = self._create_potential(potential_type)
        
        # Momentum space setup for split-step Fourier method
        self.kx = 2 * np.pi * np.fft.fftfreq(size, d=x[1]-x[0])
        self.ky = 2 * np.pi * np.fft.fftfreq(size, d=y[1]-y[0])
        self.Kx, self.Ky = np.meshgrid(self.kx, self.ky)
        self.K2 = self.Kx**2 + self.Ky**2
        
        # Time evolution operators
        self.exp_V = np.exp(-0.5j * self.V * dt / hbar)
        self.exp_K = np.exp(-0.5j * hbar * self.K2 * dt / m)
        
        # For tracking vortices
        self.vortices = []
        self.vortex_history = []
    
    def _create_potential(self, potential_type: str) -> np.ndarray:
        """Create the external potential."""
        if potential_type == 'lattice':
            # Periodic potential for supersolid formation
            k0 = 2 * np.pi / (self.L/4)  # Lattice constant
            return -2 * (np.cos(k0 * self.X) + np.cos(k0 * self.Y))
        elif potential_type == 'trap':
            # Harmonic trap
            omega = 0.1
            return 0.5 * self.m * omega**2 * (self.X**2 + self.Y**2)
        else:  # 'none'
            return np.zeros_like(self.X)
        
    def evolve(self, steps: int = 1) -> None:
        """
        Evolve the wavefunction in time using the split-step Fourier method
        with the Gross-Pitaevskii equation.
        
        Args:
            steps: Number of time steps to evolve
        """
        for _ in range(steps):
            # Nonlinear step (real space)
            psi = self.psi * np.exp(-0.5j * (self.g * np.abs(self.psi)**2 + self.V - self.mu) * self.dt / self.hbar)
            
            # Kinetic step (momentum space)
            psi_k = fft2(psi)
            psi_k *= self.exp_K
            psi = ifft2(psi_k)
            
            # Nonlinear step (real space)
            self.psi = psi * np.exp(-0.5j * (self.g * np.abs(psi)**2 + self.V - self.mu) * self.dt / self.hbar)
            
            # Track vortices
            if steps % 10 == 0:
                self._detect_vortices()
    
    def _detect_vortices(self) -> None:
        """Detect and track quantum vortices in the wavefunction."""
        phase = np.angle(self.psi)
        phase_diff_x = np.diff(phase, axis=0, append=phase[0:1, :])
        phase_diff_y = np.diff(phase, axis=1, append=phase[:, 0:1, None])
        
        # Find phase windings
        windings = np.zeros_like(phase, dtype=int)
        windings[:-1, :-1] = (np.diff(np.unwrap(phase_diff_x[:, :-1], axis=1), axis=0) > np.pi).astype(int) \
                           - (np.diff(np.unwrap(phase_diff_y[:-1, :], axis=0), axis=1) > np.pi).astype(int)
        
        # Record vortex positions
        self.vortices = np.argwhere(np.abs(windings) > 0)
        self.vortex_history.append(self.vortices.copy())
    
    def get_density(self) -> np.ndarray:
        """
        Calculate the particle density |ψ|².
        
        Returns:
            ndarray: 2D array of particle density
        """
        return np.abs(self.psi)**2
    
    def get_phase(self) -> np.ndarray:
        """
        Calculate the phase of the wavefunction.
        
        Returns:
            ndarray: 2D array of phase values in [-π, π]
        """
        return np.angle(self.psi)
    
    def get_current(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate the probability current density.
        
        Returns:
            tuple: (Jx, Jy) components of the current density
        """
        psi_conj = np.conj(self.psi)
        grad_x = np.roll(self.psi, -1, axis=1) - np.roll(self.psi, 1, axis=1)
        grad_y = np.roll(self.psi, -1, axis=0) - np.roll(self.psi, 1, axis=0)
        
        Jx = (self.hbar / (2j * self.m)) * (psi_conj * grad_x - self.psi * np.conj(grad_x))
        Jy = (self.hbar / (2j * self.m)) * (psi_conj * grad_y - self.psi * np.conj(grad_y))
        
        return np.real(Jx), np.real(Jy)

def run_visualization():
    """Run and visualize the supersolid light simulation with interactive controls."""
    # Initialize simulator with parameters for supersolid formation
    sim = SupersolidLightSimulator(
        size=256, 
        dt=0.02, 
        potential_type='lattice',
        g=5.0,  # Stronger interactions for supersolid formation
        mu=2.0  # Non-zero chemical potential
    )
    
    # Set up the figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle('Supersolid Light Simulation', fontsize=16)
    
    # Create custom colormaps
    density_cmap = 'viridis'
    phase_cmap = LinearSegmentedColormap.from_list(
        'phase', 
        ['#FF0000', '#FFFF00', '#00FF00', '#00FFFF', '#0000FF', '#FF00FF', '#FF0000']
    )
    
    # Initial plots
    density = sim.get_density()
    phase = sim.get_phase()
    Jx, Jy = sim.get_current()
    
    # Density plot
    im1 = axes[0, 0].imshow(density, cmap=density_cmap, origin='lower',
                          extent=[-sim.L/2, sim.L/2, -sim.L/2, sim.L/2])
    axes[0, 0].set_title('Density |ψ|²')
    axes[0, 0].set_xlabel('x (μm)')
    axes[0, 0].set_ylabel('y (μm)')
    fig.colorbar(im1, ax=axes[0, 0], label='Density')
    
    # Phase plot
    im2 = axes[0, 1].imshow(phase, cmap=phase_cmap, origin='lower',
                           extent=[-sim.L/2, sim.L/2, -sim.L/2, sim.L/2],
                           vmin=-np.pi, vmax=np.pi)
    axes[0, 1].set_title('Phase (arg ψ)')
    axes[0, 1].set_xlabel('x (μm)')
    axes[0, 1].set_ylabel('y (μm)')
    cbar = fig.colorbar(im2, ax=axes[0, 1])
    cbar.set_ticks([-np.pi, 0, np.pi])
    cbar.set_ticklabels(['-π', '0', 'π'])
    
    # Current plot (vector field)
    X, Y = np.meshgrid(np.linspace(-sim.L/2, sim.L/2, 15, endpoint=False),
                      np.linspace(-sim.L/2, sim.L/2, 15, endpoint=False))
    
    # Subsample the current for visualization
    step = sim.size // 15
    Jx_subsampled = Jx[::step, ::step]
    Jy_subsampled = Jy[::step, ::step]
    
    # Plot vortices if any
    if len(sim.vortices) > 0:
        vortices = np.array(sim.vortices)
        vortices = vortices * (sim.L/sim.size) - sim.L/2  # Convert to physical units
        axes[0, 1].scatter(vortices[:, 1], vortices[:, 0], c='red', s=30, marker='x')
    
    # Current plot
    current_plot = axes[1, 0].quiver(X, Y, Jx_subsampled, Jy_subsampled, 
                                    scale=0.5, scale_units='xy', angles='xy')
    axes[1, 0].set_title('Probability Current')
    axes[1, 0].set_xlabel('x (μm)')
    axes[1, 0].set_ylabel('y (μm)')
    axes[1, 0].set_xlim(-sim.L/2, sim.L/2)
    axes[1, 0].set_ylim(-sim.L/2, sim.L/2)
    
    # Fourier transform of density (structure factor)
    ft_density = np.fft.fftshift(np.abs(np.fft.fft2(density)))
    im3 = axes[1, 1].imshow(np.log(1 + ft_density), cmap='inferno', origin='lower',
                           extent=[-np.pi*sim.size/sim.L, np.pi*sim.size/sim.L,
                                  -np.pi*sim.size/sim.L, np.pi*sim.size/sim.L])
    axes[1, 1].set_title('Structure Factor (log|FFT[|ψ|²]|)')
    axes[1, 1].set_xlabel('k_x (1/μm)')
    axes[1, 1].set_ylabel('k_y (1/μm)')
    fig.colorbar(im3, ax=axes[1, 1], label='log(Intensity)')
    
    plt.tight_layout()
    
    def update(frame):
        # Evolve the system
        sim.evolve(steps=2)
        
        # Update data
        density = sim.get_density()
        phase = sim.get_phase()
        Jx, Jy = sim.get_current()
        
        # Update plots
        im1.set_array(density)
        im2.set_array(phase)
        
        # Update current plot
        Jx_subsampled = Jx[::step, ::step]
        Jy_subsampled = Jy[::step, ::step]
        
        axes[1, 0].clear()
        current_plot = axes[1, 0].quiver(X, Y, Jx_subsampled, Jy_subsampled, 
                                        scale=0.5, scale_units='xy', angles='xy')
        axes[1, 0].set_title('Probability Current')
        axes[1, 0].set_xlabel('x (μm)')
        axes[1, 0].set_ylabel('y (μm)')
        axes[1, 0].set_xlim(-sim.L/2, sim.L/2)
        axes[1, 0].set_ylim(-sim.L/2, sim.L/2)
        
        # Update structure factor
        ft_density = np.fft.fftshift(np.abs(np.fft.fft2(density)))
        im3.set_array(np.log(1 + ft_density))
        
        # Update vortices
        if len(sim.vortices) > 0:
            vortices = np.array(sim.vortices)
            vortices = vortices * (sim.L/sim.size) - sim.L/2
            axes[0, 1].scatter(vortices[:, 1], vortices[:, 0], c='red', s=30, marker='x')
        
        fig.suptitle(f'Supersolid Light Simulation (t = {frame * sim.dt * 2:.2f} ps)', 
                    fontsize=16)
        
        return im1, im2, current_plot, im3
    
    # Create animation
    print("Starting simulation...")
    ani = FuncAnimation(fig, update, frames=200, interval=50, blit=False)
    
    # Save the animation
    print("Saving animation...")
    ani.save('supersolid_light_simulation.mp4', writer='ffmpeg', 
            fps=20, dpi=150, bitrate=2000)
    print("Animation saved as 'supersolid_light_simulation.mp4'")
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_visualization()
