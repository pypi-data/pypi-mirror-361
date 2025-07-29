# File: ui_finder/viewer.py
import subprocess
import os
import platform

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
import xml.etree.ElementTree as ET
import pyperclip
from matplotlib.widgets import Button, TextBox, RadioButtons
import textwrap

def start(img_path, xml_path):
    plt.rcParams['toolbar'] = 'toolbar2'

    current_node = None
    highlight_rectangles = []
    overlapping_elements = []
    current_overlap_index = 0

    def parse_bounds(bounds_str):
        return [int(x) for x in bounds_str.replace('[', '').replace(']', ',').split(',') if x]

    def is_within_bounds(x, y, bounds):
        return bounds[0] <= x <= bounds[2] and bounds[1] <= y <= bounds[3]

    def find_all_overlapping_children(xml_file, x, y):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        nodes = []

        def parse_node(node, depth=0):
            bounds = node.get("bounds")
            if bounds:
                parsed_bounds = parse_bounds(bounds)
                if is_within_bounds(x, y, parsed_bounds):
                    nodes.append((parsed_bounds, node.attrib, depth))
            for child in node:
                parse_node(child, depth + 1)

        parse_node(root)
        nodes.sort(key=lambda x: x[2], reverse=True)
        return nodes

    def highlight_area(bounds_str):
        for rect in highlight_rectangles:
            rect.remove()
        highlight_rectangles.clear()

        if not bounds_str:
            return

        x1, y1, x2, y2 = parse_bounds(bounds_str)
        width = x2 - x1
        height = y2 - y1

        rect = patches.Rectangle((x1, y2), width, -height, linewidth=1,
                                 edgecolor='blue', facecolor='cyan', linestyle='--', alpha=0.5)
        ax_img.add_patch(rect)
        highlight_rectangles.append(rect)
        plt.draw()

    def onclick(event):
        nonlocal current_node, overlapping_elements, current_overlap_index

        if event.inaxes == ax_img:
            x, y = event.xdata, event.ydata
            print(f"Clicked at ({x:.2f}, {y:.2f})")

            overlapping_elements = find_all_overlapping_children(xml_path, x, y)
            current_overlap_index = 0

            if overlapping_elements:
                bounds, attributes, _ = overlapping_elements[current_overlap_index]
                current_node = attributes
                highlight_area(str(bounds))
                display_attributes(current_node)

                selected = display_attributes.dropdown.value_selected
                on_dropdown_change(selected)
            else:
                print("No matching XML element.")
                display_attributes(None)

    def on_key_press(event):
        nonlocal current_node, overlapping_elements, current_overlap_index

        if event.key == 'n' and overlapping_elements:
            current_overlap_index = (current_overlap_index + 1) % len(overlapping_elements)
            bounds, attributes, _ = overlapping_elements[current_overlap_index]
            current_node = attributes
            highlight_area(str(bounds))
            display_attributes(current_node)

            selected = display_attributes.dropdown.value_selected
            on_dropdown_change(selected)

    def on_dropdown_change(label):
        if not current_node:
            return

        if label == 'Class':
            value = f'className={current_node.get("class")}'
        elif label == 'Resource ID':
            value = f'resourceId={current_node.get("resource-id")}'
        elif label == 'Text':
            value = f'text={current_node.get("text")}'
        elif label == 'Bound':
            value = f'bounds={current_node.get("bounds")}'
        else:
            value = ''

        display_attributes.textbox2.set_val('')
        display_attributes.textbox2.set_val(value)

    def display_attributes(attributes):
        ax_attr.clear()

        if attributes:
            lines = [f"{k}: {textwrap.fill(v, 30)}" for k, v in attributes.items()]
            display_text = '\n'.join(lines)

            ax_attr.text(0.05, 0.99, display_text, ha='left', va='top', fontsize=10, fontfamily='Georgia',
                         color='#EAEAEA', transform=ax_attr.transAxes,
                         bbox=dict(facecolor='#2D2D2D', edgecolor='#1C1C1C', boxstyle='round,pad=0.5'))
        else:
            ax_attr.text(0.5, 0.5, "No attributes found", ha='center', va='center', fontsize=10, color='red',
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=1.0'))

        ax_attr.set_xticks([])
        ax_attr.set_yticks([])
        for spine in ax_attr.spines.values():
            spine.set_visible(False)

        if not hasattr(display_attributes, 'textbox2'):
            textbox2_ax = plt.axes([0.5, 0.18, 0.45, 0.05], facecolor='gray')
            display_attributes.textbox2 = TextBox(textbox2_ax, '', initial='')
            display_attributes.textbox2.text_disp.set_fontsize(9)
            display_attributes.textbox2.text_disp.set_fontfamily('Georgia')
            display_attributes.textbox2.text_disp.set_color('darkblue')

            dropdown_ax = plt.axes([0.6, 0.28, 0.3, 0.12], facecolor='lightgoldenrodyellow')
            display_attributes.dropdown = RadioButtons(dropdown_ax, ['Class', 'Resource ID', 'Text', 'Bound'])
            display_attributes.dropdown.on_clicked(on_dropdown_change)

            copy_button_ax = plt.axes([0.6, 0.05, 0.3, 0.05])
            copy_button = Button(copy_button_ax, 'Copy to Clipboard', color='lightblue', hovercolor='lightgreen')
            copy_button.label.set_fontsize(10)

            def on_copy_button_click(event):
                def reset():
                    if copy_button.label.get_text() != "Copy to Clipboard":
                        copy_button.label.set_text("Copy to Clipboard")
                        fig.canvas.draw_idle()

                try:
                    fig.canvas.widgetlock.release(None)
                    content = display_attributes.textbox2.text.strip()
                    if content:
                        pyperclip.copy(content)
                        print("Copied to clipboard:", content)
                        copy_button.label.set_text("Copied")
                        fig.canvas.draw_idle()

                        timer = fig.canvas.new_timer(interval=1500)
                        timer.add_callback(reset)
                        timer.start()
                except RuntimeError as e:
                    if "Another Axes already grabs mouse input" in str(e):
                        print("Ignored widget conflict.")
                    else:
                        print("Unexpected error:", e)

            copy_button.on_clicked(on_copy_button_click)

    fig, (ax_img, ax_attr) = plt.subplots(1, 2, figsize=(6.8, 6), gridspec_kw={'width_ratios': [5, 5]})

    try:
        fig.canvas.manager.window.setWindowTitle('Android UI Inspector')
    except:
        fig.canvas.manager.window.wm_title('Android UI Inspector')

    background_img = mpimg.imread(img_path)
    image_height, image_width, _ = background_img.shape

    ax_img.imshow(background_img, extent=[0, image_width, image_height, 0])
    ax_img.set_title('Main Image')
    ax_img.add_patch(patches.Rectangle((0, 0), image_width, image_height, linewidth=2, edgecolor='black', facecolor='none'))

    for ax in [ax_img, ax_attr]:
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    fig.canvas.mpl_connect('button_press_event', onclick)
    fig.canvas.mpl_connect('key_press_event', on_key_press)

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    start("screenshot.png", "dump.xml")
