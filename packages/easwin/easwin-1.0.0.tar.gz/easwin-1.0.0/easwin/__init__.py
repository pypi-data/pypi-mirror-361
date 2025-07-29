import tkinter as tk
import base64
import io
import pygame
import tkinter.font as tkFont
pygame.init()

_stored_key_handler = None
_stored_mouse_handler = None

class mouse:
    @staticmethod
    def game(left=None, right=None, wheel=None, wheel_up=None, wheel_down=None):
        global _stored_mouse_handler
        mouse_map = {
            pygame.BUTTON_WHEELDOWN: wheel_down, pygame.BUTTON_WHEELUP: wheel_up,
            pygame.BUTTON_MIDDLE: wheel,
            pygame.BUTTON_RIGHT: right, pygame.BUTTON_LEFT: left,
        }
        def handle_mouse(event, running):
            if event.type == pygame.MOUSEBUTTONDOWN:
                cb = mouse_map.get(event.button)
                if callable(cb):
                    result = cb(running)
                    if result is not None:
                        return result
            return running
        _stored_mouse_handler = handle_mouse
        return handle_mouse

    @staticmethod
    def soft(left=None, right=None, wheel=None, wheel_up=None, wheel_down=None):
        global _stored_mouse_handler
        def handle_mouse(widget):
            def on_left_click(event):
                if isinstance(event.widget, tk.Button):
                    return
                if left is not None:
                    left(True)
            def on_right_click(event):
                if isinstance(event.widget, tk.Button):
                    return
                if right is not None:
                    right(True)
            def on_middle_click(event):
                if isinstance(event.widget, tk.Button):
                    return
                if wheel is not None:
                    wheel(True)
            def on_mouse_wheel(e):
                if isinstance(e.widget, tk.Button):
                    return
                delta = 0
                if e.num == 4:
                    delta = 1
                elif e.num == 5:
                    delta = -1
                elif hasattr(e, 'delta'):
                    delta = e.delta
                if delta > 0:
                    if wheel_up:
                        wheel_up(True)
                    elif wheel:
                        wheel(True)
                elif delta < 0:
                    if wheel_down:
                        wheel_down(True)
                    elif wheel:
                        wheel(True)
            if left is not None:
                widget.bind('<Button-1>', on_left_click)
            if right is not None:
                widget.bind('<Button-3>', on_right_click)
            if wheel is not None:
                widget.bind('<Button-2>', on_middle_click)
            if wheel_up is not None or wheel_down is not None or wheel is not None:
                widget.bind('<Button-4>', on_mouse_wheel)
                widget.bind('<Button-5>', on_mouse_wheel)
                widget.bind('<MouseWheel>', on_mouse_wheel)
        _stored_mouse_handler = handle_mouse
        return handle_mouse

class key:
    @staticmethod
    def game(
        space=None, a=None, b=None, c=None, d=None, e=None, f=None, g=None, h=None, i=None, j=None, k=None, l=None, m=None,
        n=None, o=None, p=None, q=None, r=None, s=None, t=None, u=None, v=None, w=None, x=None, y=None, z=None,
        one=None, two=None, three=None, four=None, five=None, six=None, seven=None, eight=None, nine=None, zero=None,
        enter=None, escape=None, tab=None, backspace=None, up=None, down=None, left=None, right=None,
        comma=None, period=None, semicolon=None, quote=None, minus=None, equals=None, slash=None,
        backslash=None, leftbracket=None, rightbracket=None, backquote=None,
        f1=None, f2=None, f3=None, f4=None, f5=None, f6=None, f7=None, f8=None, f9=None, f10=None, f11=None, f12=None
    ):
        global _stored_key_handler
        key_map = {
            pygame.K_SPACE: space, pygame.K_a: a, pygame.K_b: b, pygame.K_c: c, pygame.K_d: d,
            pygame.K_e: e, pygame.K_f: f, pygame.K_g: g, pygame.K_h: h, pygame.K_i: i,
            pygame.K_j: j, pygame.K_k: k, pygame.K_l: l, pygame.K_m: m, pygame.K_n: n,
            pygame.K_o: o, pygame.K_p: p, pygame.K_q: q, pygame.K_r: r, pygame.K_s: s,
            pygame.K_t: t, pygame.K_u: u, pygame.K_v: v, pygame.K_w: w, pygame.K_x: x,
            pygame.K_y: y, pygame.K_z: z, pygame.K_1: one, pygame.K_2: two, pygame.K_3: three,
            pygame.K_4: four, pygame.K_5: five, pygame.K_6: six, pygame.K_7: seven, pygame.K_8: eight,
            pygame.K_9: nine, pygame.K_0: zero, pygame.K_RETURN: enter, pygame.K_ESCAPE: escape,
            pygame.K_TAB: tab, pygame.K_BACKSPACE: backspace, pygame.K_UP: up, pygame.K_DOWN: down,
            pygame.K_LEFT: left, pygame.K_RIGHT: right, pygame.K_COMMA: comma, pygame.K_PERIOD: period,
            pygame.K_SEMICOLON: semicolon, pygame.K_QUOTE: quote, pygame.K_MINUS: minus,
            pygame.K_EQUALS: equals, pygame.K_SLASH: slash, pygame.K_BACKSLASH: backslash,
            pygame.K_LEFTBRACKET: leftbracket, pygame.K_RIGHTBRACKET: rightbracket,
            pygame.K_BACKQUOTE: backquote,
            pygame.K_F1: f1, pygame.K_F2: f2, pygame.K_F3: f3, pygame.K_F4: f4, pygame.K_F5: f5,
            pygame.K_F6: f6, pygame.K_F7: f7, pygame.K_F8: f8, pygame.K_F9: f9, pygame.K_F10: f10,
            pygame.K_F11: f11, pygame.K_F12: f12,
        }
        def handle_keys(event, running):
            if event.type == pygame.KEYDOWN:
                cb = key_map.get(event.key)
                if callable(cb):
                    result = cb(running)
                    if result is not None:
                        return result
            return running
        _stored_key_handler = handle_keys
        return handle_keys

    @staticmethod
    def soft(
            space=None, a=None, b=None, c=None, d=None, e=None, f=None, g=None, h=None, i=None, j=None, k=None, l=None,
            m=None, n=None, o=None, p=None, q=None, r=None, s=None, t=None, u=None, v=None, w=None, x=None, y=None, z=None,
            one=None, two=None, three=None, four=None, five=None, six=None, seven=None, eight=None, nine=None, zero=None,
            enter=None, escape=None, tab=None, backspace=None, up=None, down=None, left=None, right=None,
            comma=None, period=None, semicolon=None, quote=None, minus=None, equals=None, slash=None,
            backslash=None, leftbracket=None, rightbracket=None, backquote=None,
            f1=None, f2=None, f3=None, f4=None, f5=None, f6=None, f7=None, f8=None, f9=None, f10=None, f11=None,
            f12=None
    ):
        global _stored_key_map, _stored_key_handler
        _stored_key_map = {
            'space': space, 'a': a, 'b': b, 'c': c, 'd': d, 'e': e, 'f': f, 'g': g, 'h': h, 'i': i, 'j': j, 'k': k,
            'l': l, 'm': m, 'n': n, 'o': o, 'p': p, 'q': q, 'r': r, 's': s, 't': t, 'u': u, 'v': v, 'w': w, 'x': x,
            'y': y, 'z': z, '1': one, '2': two, '3': three, '4': four, '5': five, '6': six, '7': seven, '8': eight,
            '9': nine, '0': zero, 'Return': enter, 'Escape': escape, 'Tab': tab, 'BackSpace': backspace,
            'Up': up, 'Down': down, 'Left': left, 'Right': right, ',': comma, '.': period, ';': semicolon,
            "'": quote, '-': minus, '=': equals, '/': slash, '\\': backslash, '[': leftbracket, ']': rightbracket,
            '`': backquote, 'F1': f1, 'F2': f2, 'F3': f3, 'F4': f4, 'F5': f5, 'F6': f6,
            'F7': f7, 'F8': f8, 'F9': f9, 'F10': f10, 'F11': f11, 'F12': f12
        }
        def handle_keys(event):
            cb = _stored_key_map.get(event.keysym)
            if callable(cb):
                cb(True)
        _stored_key_handler = handle_keys
        return handle_keys

ima = """iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8zwUAAg4BC+kXXYkAAAAASUVORK5CYII="""

class Window:
    @staticmethod
    def soft(title="your window", width=500, height=500, resizable=False, color="white", icon=ima, setup=None):
        global _stored_key_handler
        root = tk.Tk()
        root.config(bg=color)
        Window.root0 = root
        if setup is not None:
            setup()
        if icon is not None:
            try:
                if "." in icon[-6:]:
                    if icon.endswith(".ico"):
                        root.iconbitmap(icon)
                    else:
                        photo = tk.PhotoImage(file=icon)
                        root.iconphoto(False, photo)
                else:
                    photo = tk.PhotoImage(data=icon)
                    root.iconphoto(False, photo)
            except Exception:
                pass
        if not resizable:
            root.resizable(False, False)
        root.title(title)
        root.geometry(f'{width}x{height}')
        if _stored_key_handler is not None:
            root.bind("<KeyPress>", _stored_key_handler)
        if _stored_mouse_handler is not None:
            _stored_mouse_handler(root)
        root.mainloop()

    @staticmethod
    def game(
            title="your window", width=500, height=500, resizable=False, color="white", icon=ima,
            key_handler=None, mouse_handler=None, fps=60, img=None, x=0, y=0, img_width=100, img_height=100,):
        pygame.init()
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE if resizable else 0)
        pygame.display.set_caption(title)
        if img is not None:
            image = pygame.image.load(img)
        if icon:
            if "." in icon[-6:]:
                icon_surface = pygame.image.load(icon)
            else:
                icon_bytes = base64.b64decode(icon)
                icon_stream = io.BytesIO(icon_bytes)
                icon_surface = pygame.image.load(icon_stream)
            pygame.display.set_icon(icon_surface)
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        handler = key_handler if key_handler else _stored_key_handler
                        if handler:
                            new_running = handler(event, running)
                            if new_running is not None:
                                running = new_running
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    handler = mouse_handler if mouse_handler else _stored_mouse_handler
                    if handler:
                        new_running = handler(event, running)
                        if new_running is not None:
                            running = new_running
                elif event.type == pygame.VIDEORESIZE:
                    width, height = event.w, event.h
                    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            screen.fill(color)
            if img is not None:
                image = pygame.transform.scale(image, (img_width, img_height))
                screen.blit(image, (x, y))
            pygame.display.flip()
            clock.tick(fps)
        pygame.quit()

class soft:
    @staticmethod
    def button(text="Click me", fonc=None, family='arial', size=20, width=30, height=5, weight='normal', color='white', text_color='black', x=0, y=0):
        root = tk.Tk()
        font = tkFont.Font(family=family, size=size, weight=weight)
        button = tk.Button(root, text=text, font=font, bg=color, fg=text_color, width=width, height=height, command=fonc)
        button.place(x=x, y=y)
        root.mainloop()
