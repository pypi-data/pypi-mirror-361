from PyQt6.QtWidgets import QApplication, QMainWindow
import matplotlib.pyplot as plt
import copy
import numpy as np


class PaintManager(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.resume = False

    def get_line_points(self, x0, y0, x1, y1):
        """Get all points in a line between (x0,y0) and (x1,y1) using Bresenham's algorithm."""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                points.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                points.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
                
        points.append((x, y))
        return points

    def initiate_paint_session(self, channel, current_xlim, current_ylim):
        # Create static background (same as selection rectangle)

        if self.parent().machine_window is not None:
            if self.parent().machine_window.segmentation_worker is not None:
                if not self.parent().machine_window.segmentation_worker._paused:
                    self.resume = True
                self.parent().machine_window.segmentation_worker.pause()


        if not self.parent().channel_visible[channel]:
            self.parent().channel_visible[channel] = True
            
        # Capture the background once
        self.parent().static_background = self.parent().canvas.copy_from_bbox(self.parent().ax.bbox)

        if self.resume:
            self.parent().machine_window.segmentation_worker.resume()
            self.resume = False



    def start_virtual_paint_session(self, channel, current_xlim, current_ylim):
        """Start a virtual paint session that doesn't modify arrays until the end."""
        self.parent().painting = True
        self.parent().paint_channel = channel
        
        # Store original state
        if not self.parent().channel_visible[channel]:
            self.parent().channel_visible[channel] = True
            
        # Initialize virtual paint storage - separate draw and erase operations
        self.parent().virtual_draw_operations = []  # Stores drawing operations
        self.parent().virtual_erase_operations = []  # Stores erase operations
        self.parent().current_operation = []
        self.parent().current_operation_type = None  # 'draw' or 'erase'

    def add_virtual_paint_point(self, x, y, brush_size, erase=False, foreground=True):
        """Add a single paint point to the virtual layer."""
        
        # Determine operation type and visual properties
        if erase:
            paint_color = 'black'  # Visual indicator for erase
            alpha = 0.5
            operation_type = 'erase'
        else:
            if self.parent().machine_window is not None:
                if foreground:
                    paint_color = 'green'  # Visual for foreground (value 1)
                    alpha = 0.7
                else:
                    paint_color = 'red'  # Visual for background (value 2)
                    alpha = 0.7
            else:
                paint_color = 'white'  # Normal paint
                alpha = 0.7
            operation_type = 'draw'
                
        # Store the operation data (for later conversion to real paint)
        operation_data = {
            'x': x,
            'y': y,
            'brush_size': brush_size,
            'erase': erase,
            'foreground': foreground,
            'channel': self.parent().paint_channel,
            'threed': getattr(self.parent(), 'threed', False),
            'threedthresh': getattr(self.parent(), 'threedthresh', 1)
        }
        
        # Create visual circle
        circle = plt.Circle((x, y), brush_size/2, 
                           color=paint_color, alpha=alpha, animated=True)
        
        # Add to current operation
        if self.parent().current_operation_type != operation_type:
            # Finish previous operation if switching between draw/erase
            self.finish_current_virtual_operation()
            self.parent().current_operation_type = operation_type
        
        self.parent().current_operation.append({
            'circle': circle,
            'data': operation_data
        })
        
        self.parent().ax.add_patch(circle)

    def add_virtual_paint_stroke(self, x, y, brush_size, erase=False, foreground=True):
        """Add a paint stroke - simple visual, interpolation happens during data conversion."""
        # Just add the current point for visual display (no interpolation yet)
        self.add_virtual_paint_point(x, y, brush_size, erase, foreground)
        
        # Store the last position for data conversion later
        self.parent().last_virtual_pos = (x, y)

    def finish_current_virtual_operation(self):
        """Finish the current operation (draw or erase) and add it to the appropriate list."""
        
        if not self.parent().current_operation:
            return
            
        if self.parent().current_operation_type == 'draw':
            self.parent().virtual_draw_operations.append(self.parent().current_operation)
        elif self.parent().current_operation_type == 'erase':
            self.parent().virtual_erase_operations.append(self.parent().current_operation)
        
        self.parent().current_operation = []
        self.parent().current_operation_type = None

    def update_virtual_paint_display(self):
        """Update display with virtual paint strokes - super fast like selection rectangle."""
        if not hasattr(self.parent(), 'static_background') or self.parent().static_background is None:
            return
        
        # Restore the clean background
        self.parent().canvas.restore_region(self.parent().static_background)
        
        # Draw all completed operations
        for operation_list in [self.parent().virtual_draw_operations, self.parent().virtual_erase_operations]:
            for operation in operation_list:
                for item in operation:
                    self.parent().ax.draw_artist(item['circle'])
        
        # Draw current operation being painted
        if hasattr(self.parent(), 'current_operation'):
            for item in self.parent().current_operation:
                self.parent().ax.draw_artist(item['circle'])
        
        # Blit everything at once
        self.parent().canvas.blit(self.parent().ax.bbox)

    def convert_virtual_strokes_to_data(self):
        """Convert virtual paint strokes to actual array data with interpolation applied here."""
        
        # First, apply all drawing operations with interpolation
        for operation in self.parent().virtual_draw_operations:
            last_pos = None
            for item in operation:
                data = item['data']
                current_pos = (data['x'], data['y'])
                
                if last_pos is not None:
                    points = self.get_line_points(last_pos[0], last_pos[1], current_pos[0], current_pos[1])
                    for px, py in points:
                        self.paint_at_position_vectorized(
                            px, py,
                            erase=False,
                            channel=data['channel'],
                            brush_size=data['brush_size'],
                            threed=data['threed'],  # Add this
                            threedthresh=data['threedthresh'],  # Add this
                            foreground=data['foreground'],
                            machine_window=self.parent().machine_window
                        )
                else:
                    self.paint_at_position_vectorized(
                        data['x'], data['y'],
                        erase=False,
                        channel=data['channel'],
                        brush_size=data['brush_size'],
                        threed=data['threed'],  # Add this
                        threedthresh=data['threedthresh'],  # Add this
                        foreground=data['foreground'],
                        machine_window=self.parent().machine_window
                    )
                
                last_pos = current_pos
                try:
                    item['circle'].remove()
                except:
                    pass
        
        # Then, apply all erase operations with interpolation (same changes)
        for operation in self.parent().virtual_erase_operations:
            last_pos = None
            for item in operation:
                data = item['data']
                current_pos = (data['x'], data['y'])
                
                if last_pos is not None:
                    points = self.get_line_points(last_pos[0], last_pos[1], current_pos[0], current_pos[1])
                    for px, py in points:
                        self.paint_at_position_vectorized(
                            px, py,
                            erase=True,
                            channel=data['channel'],
                            brush_size=data['brush_size'],
                            threed=data['threed'],  # Add this
                            threedthresh=data['threedthresh'],  # Add this
                            foreground=data['foreground'],
                            machine_window=self.parent().machine_window
                        )
                else:
                    self.paint_at_position_vectorized(
                        data['x'], data['y'],
                        erase=True,
                        channel=data['channel'],
                        brush_size=data['brush_size'],
                        threed=data['threed'],  # Add this
                        threedthresh=data['threedthresh'],  # Add this
                        foreground=data['foreground'],
                        machine_window=self.parent().machine_window
                    )
                
                last_pos = current_pos
                try:
                    item['circle'].remove()
                except:
                    pass
        
        # Clean up
        self.parent().virtual_draw_operations = []
        self.parent().virtual_erase_operations = []
        if hasattr(self.parent(), 'current_operation'):
            for item in self.parent().current_operation:
                try:
                    item['circle'].remove()
                except:
                    pass
            self.parent().current_operation = []
        self.parent().current_operation_type = None


    def end_virtual_paint_session(self):
        """Convert virtual paint to actual array modifications when exiting paint mode."""
        if not hasattr(self.parent(), 'virtual_paint_strokes'):
            return
        
        # Now apply all the virtual strokes to the actual arrays
        for stroke in self.parent().virtual_paint_strokes:
            for circle in stroke:
                center = circle.center
                radius = circle.radius
                is_erase = circle.get_facecolor()[0] == 0  # Black = erase
                
                # Apply to actual array
                self.paint_at_position_vectorized(
                    int(center[0]), int(center[1]), 
                    erase=is_erase, 
                    channel=self.paint_channel,
                    brush_size=int(radius * 2)
                )
                
                # Remove the virtual circle
                circle.remove()
        
        # Clean up virtual paint data
        self.virtual_paint_strokes = []
        self.current_stroke = []
        
        # Reset background
        self.static_background = None
        self.painting = False
        
        # Full refresh to show final result
        self.update_display()

    def paint_at_position_vectorized(self, center_x, center_y, erase=False, channel=2, 
                                   slice_idx=None, brush_size=None, threed=None, 
                                   threedthresh=None, foreground=True, machine_window=None):
        """Vectorized paint operation for better performance."""
        if self.parent().channel_data[channel] is None:
            return
        
        # Use provided parameters or fall back to instance variables
        slice_idx = slice_idx if slice_idx is not None else self.parent().current_slice
        brush_size = brush_size if brush_size is not None else getattr(self.parent(), 'brush_size', 5)
        threed = threed if threed is not None else getattr(self.parent(), 'threed', False)
        threedthresh = threedthresh if threedthresh is not None else getattr(self.parent(), 'threedthresh', 1)
        
        # Handle 3D painting by recursively calling for each slice
        if threed and threedthresh > 1:
            half_range = (threedthresh - 1) // 2
            low = max(0, slice_idx - half_range)
            high = min(self.parent().channel_data[channel].shape[0] - 1, slice_idx + half_range)
            
            
            for i in range(low, high + 1):
                
                # Recursive call for each slice, but with threed=False to avoid infinite recursion
                self.paint_at_position_vectorized(
                    center_x, center_y, 
                    erase=erase, 
                    channel=channel,
                    slice_idx=i,  # Paint on slice i
                    brush_size=brush_size,
                    threed=False,  # Important: turn off 3D for recursive calls
                    threedthresh=1,
                    foreground=foreground,
                    machine_window=machine_window
                )
                
                
            return  # Exit early, recursive calls handle everything
        
        # Regular 2D painting (single slice)
        
        # Determine paint value
        if erase:
            val = 0
        elif machine_window is None:
            try:
                val = self.parent().min_max[channel][1]
            except:
                val = 255
        elif foreground:
            val = 1
        else:
            val = 2
        
        height, width = self.parent().channel_data[channel][slice_idx].shape
        radius = brush_size // 2
        
        # Calculate affected region bounds
        y_min = max(0, center_y - radius)
        y_max = min(height, center_y + radius + 1)
        x_min = max(0, center_x - radius)
        x_max = min(width, center_x + radius + 1)
        
        if y_min >= y_max or x_min >= x_max:
            return  # No valid region to paint
        
        # Create coordinate grids for the affected region
        y_coords, x_coords = np.mgrid[y_min:y_max, x_min:x_max]
        
        # Calculate distances squared (avoid sqrt for performance)
        distances_sq = (x_coords - center_x) ** 2 + (y_coords - center_y) ** 2
        mask = distances_sq <= radius ** 2
        
        # Paint on this single slice
        
        self.parent().channel_data[channel][slice_idx][y_min:y_max, x_min:x_max][mask] = val