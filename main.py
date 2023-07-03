import arcade
import random
import time

WIDTH = 400
HEIGHT = 1000
TILE_WIDTH = 100
TILE_HEIGHT = 250
TIMEOUT_CONSTANT = 2
TOTAL_GAME_TIME = 20
PAUSE_SCREEN_TRANSPARENCY = 150
TEXT_OFFSET = 50
TITLE = "Funky piano game"


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.height = HEIGHT
        self.width = WIDTH

        self.current_y = 0

        self.cam = None
        self.reset_cam = None
        self.gui_cam = None

        self.tiles = None
        self.tiles_list = []
        self.score_list = None
        self.reset_layer = None

        self.score = 0

        self.timeout = False
        self.timeout_start = 0
        self.keys_pressed_since_reset = 0

        self.timer_started = False
        self.timer_starting_time = 0

        self.red_tile_num = None

        arcade.set_background_color(arcade.csscolor.WHITE)

    def setup(self):
        self.cam = arcade.Camera(self.width, self.height)
        self.gui_cam = arcade.Camera(self.width, self.height)
        self.reset_cam = arcade.Camera(self.width, self.height)

        self.tiles = arcade.SpriteList()
        self.reset_layer = arcade.SpriteList()
        self.score_list = arcade.SpriteList()

        score_box = arcade.Sprite("blue1.jpg")
        score_box.right = 400
        score_box.top = 1000
        self.score_list.append(score_box)

        for i in range(4):
            if i == 0:
                tile = arcade.Sprite("black2.jpg")
            else:
                tile = arcade.Sprite("black1.jpg")
            slot_num = random.randint(0, 3)
            self.tiles_list.append(slot_num + 1)
            tile.left = slot_num * 100
            tile.bottom = self.current_y
            self.current_y += 250
            self.tiles.append(tile)

    def on_show_view(self):
        self.setup()

    def on_draw(self):
        self.clear()
        self.cam.use()
        self.tiles.draw()

        self.reset_cam.use()
        self.reset_layer.draw()

        self.gui_cam.use()

        self.score_list.draw()
        score_text = str(self.score)
        arcade.draw_text(
            score_text,
            365,
            970,
            arcade.csscolor.WHITE,
            12,
        )

    def update_tiles(self):
        if not self.timer_started:
            self.timer_started = True
            self.timer_starting_time = time.time()
        self.tiles_list.pop(0)
        self.score += 1
        self.add_new_tile()

    def add_new_tile(self):
        self.keys_pressed_since_reset += 1
        tile = arcade.Sprite("black1.jpg")
        slot_num = random.randint(0, 3)
        self.tiles_list.append(slot_num + 1)
        tile.left = slot_num * 100
        tile.bottom = self.current_y
        self.current_y += 250
        self.tiles.append(tile)

    def restart(self):
        self.keys_pressed_since_reset = 0
        tile_num = self.tiles_list[0]
        start = arcade.Sprite("black2.jpg")
        start.left = tile_num * 100 - 100
        start.bottom = self.current_y - 1000
        self.reset_layer.append(start)

    def add_reset_tile(self, name, tile_num):
        tile = arcade.Sprite(name)
        tile.left = tile_num * 100
        tile.bottom = self.current_y - 1000
        self.reset_layer.append(tile)

    def update_high_score(self):
        f = open("scores.txt")
        high_score = f.read()
        f.close()
        if high_score == "":
            f = open("scores.txt", "w")
            f.write(str(self.score))
            f.close()
        elif self.score > int(high_score):
            f = open("scores.txt", "w")
            f.write(str(self.score))
            f.close()

    def on_key_press(self, key, modifiers):
        t = time.time()
        if not self.timeout or t - self.timeout_start >= TIMEOUT_CONSTANT:
            if key == arcade.key.KEY_1 and self.tiles_list[0] == 1:
                self.update_tiles()
                print(1)
            elif key == arcade.key.KEY_2 and self.tiles_list[0] == 2:
                self.update_tiles()
                print(2)
            elif key == arcade.key.KEY_3 and self.tiles_list[0] == 3:
                self.update_tiles()
                print(3)
            elif key == arcade.key.KEY_4 and self.tiles_list[0] == 4:
                self.update_tiles()
                print(4)
            else:
                if self.keys_pressed_since_reset != 0:
                    # add red here
                    self.timeout = True
                    self.timeout_start = time.time()
                    print("Timeout")
                    if key == arcade.key.KEY_1:
                        tile_num = 0
                    elif key == arcade.key.KEY_2:
                        tile_num = 1
                    elif key == arcade.key.KEY_3:
                        tile_num = 2
                    else:
                        tile_num = 3

                    self.red_tile_num = tile_num
                    self.add_reset_tile("red1.png", tile_num)

        else:
            print(time.time() - self.timeout_start)

    def adjust_camera(self):
        screen_center_x = 0
        screen_center_y = self.current_y - 1000

        player_centered = screen_center_x, screen_center_y
        self.cam.move_to(player_centered, 0.2)
        self.reset_cam.move_to(player_centered, 0.2)

    def on_update(self, delta_time):
        self.adjust_camera()

        if (
            time.time() - self.timer_starting_time >= TOTAL_GAME_TIME
            and self.timer_started
        ):
            self.update_high_score()
            window = self.window

            level_finished = Finished(self, arcade.color.WHITE, self.score)
            window.show_view(level_finished)

        if (
            time.time() - self.timeout_start >= TIMEOUT_CONSTANT
            and self.timeout
        ):
            self.timeout = False
            self.reset_layer.pop()
            self.restart()


class Finished(arcade.View):
    def __init__(self, game_view, fill_colour, score):
        super().__init__()

        self.score = score
        self.game_view = game_view
        self.fill_color = arcade.make_transparent_color(
            fill_colour, transparency=PAUSE_SCREEN_TRANSPARENCY
        )

    def get_highscore(self):
        f = open("scores.txt")
        score = f.read()
        f.close()
        return score

    def on_draw(self):
        self.clear()
        self.game_view.on_draw()

        high_score = self.get_highscore()

        arcade.draw_lrtb_rectangle_filled(
            left=0,
            right=WIDTH,
            top=HEIGHT,
            bottom=0,
            color=self.fill_color,
        )

        arcade.draw_text(
            f"Score: {self.score}",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.BLACK,
            font_size=50,
            anchor_x="center",
        )

        arcade.draw_text(
            f"High Score: {high_score}",
            self.window.width / 2,
            self.window.height / 2 - TEXT_OFFSET,
            arcade.color.BLACK,
            font_size=20,
            anchor_x="center",
        )

        arcade.draw_text(
            "Click to play again",
            self.window.width / 2,
            self.window.height / 2 - 2 * TEXT_OFFSET,
            arcade.color.BLACK,
            font_size=20,
            anchor_x="center",
        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        view = GameView()
        self.window.show_view(view)


def main():
    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    game_view = GameView()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
