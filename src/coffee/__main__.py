import asyncio
from dataclasses import dataclass
from decimal import Decimal

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll, Center
from textual.events import Resize
from textual.widgets import (
    Button,
    Input,
    Static,
    Label,
    ContentSwitcher,
    Markdown,
)
from textual.reactive import reactive


ABOUT_MD = """\
### About

This was a Sunday afternoon coding session, just for fun.
It has no connection to terminal.shop.

Brought to you by @willmcgugan, head code monkey at Textualize.
"""


@dataclass
class Product:
    name: str
    sku: str
    price: Decimal
    description: str


PRODUCTS = [
    Product(
        name="nil blend coffee",
        sku="whole bean | medium roast | 12oz",
        price=Decimal("25"),
        description="Dive into the rich taste of Nil, our delicious semi-sweet coffee with notes of chocolate, peanut butter, and a hint of fig.",
    ),
    Product(
        name="None blend coffee",
        sku="whole bean | light roast | 500g",
        price=Decimal("19.95"),
        description="Delicious honey method coffee, with hints of caramel",
    ),
]


@dataclass
class Question:
    q: str
    a: str


FAQS = [
    Question(
        "where do you ship?",
        "We don't ship. But if you visit @willmcgugan, he may make you a cup of coffee.",
    ),
    Question(
        "is your coffee ethically sourced?",
        "Not sure. I get it from the place around the corner.",
    ),
    Question(
        "is ordering via ssh secure?", "it is. But you can't order anything from here."
    ),
    Question(
        "how do you store my data?",
        "We don't store anything. Close the browser and it is though we never met.",
    ),
    Question(
        "I only want to drink Nil / None, do you offer a subscription?",
        "The coffee is made up, so no, we don't offer a subscription.",
    ),
    Question(
        "Will Nil / None make me a better developer?",
        "Coffee is known to give super-human coding prowess. So yes.",
    ),
    Question(
        "Does coffee from the command line taste better than regular coffee?",
        "Depends on your shell and OS.",
    ),
]


class Column(Vertical):
    pass


class NonFocusableVerticalScroll(VerticalScroll, can_focus=False):
    pass


class Footer(Horizontal):
    def compose(self) -> ComposeResult:
        yield Label("Footer goes here")


class Panel(Vertical):
    def __init__(self, label: str, id: str) -> None:
        self.label = label
        super().__init__(id=id)

    def compose(self) -> ComposeResult:
        yield VerticalScroll(classes="content")
        yield Footer()


class OrderCounter(Horizontal):
    order_count = reactive(0, recompose=True)

    def compose(self) -> ComposeResult:
        yield Label("-", classes="minus")
        yield Label(str(self.order_count), classes="count")
        yield Label("+", classes="plus")


class ProductWidget(Vertical, can_focus=True):
    order_count: reactive[int] = reactive(0)

    BINDINGS = [
        ("minus", "order(-1)"),
        ("plus", "order(+1)"),
    ]

    def __init__(self, product: Product, classes: str) -> None:
        self.product = product
        super().__init__(classes=classes)

    def compose(self) -> ComposeResult:
        yield Static(self.product.name, classes="name")
        yield Static(self.product.sku, classes="sku")
        yield Static(f"${self.product.price:.02f}", classes="price")
        yield Static(self.product.description, classes="description")
        yield OrderCounter().data_bind(ProductWidget.order_count)

    def action_order(self, delta: int) -> None:
        self.order_count = max(0, self.order_count + delta)


class ProductsPanel(Vertical):
    def compose(self) -> ComposeResult:
        with NonFocusableVerticalScroll():
            for product in PRODUCTS:
                yield ProductWidget(product, classes="auto-focus")

        yield Label(
            "[b]tab[/] [dim]next product[/]   [b]+[/] [dim]add[/dim]   [b]-[/] [dim]remove[/dim]   [b]c[/] [dim]cart[/]   [b]q[/] [dim]quit[/dim]",
            classes="footer",
        )


class AboutPanel(Vertical):
    def compose(self) -> ComposeResult:
        with Vertical(classes="content auto-focus"):
            yield Markdown(ABOUT_MD)
        yield Label("[b]↑↓[/] [dim]scroll[/]   [b]c[/] [dim]cart[/]", classes="footer")


class FAQPanel(Vertical):
    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="content auto-focus"):
            for question in FAQS:
                yield Static(question.q, classes="question")
                yield Static(question.a, classes="answer")

        yield Label(
            "[b]↑↓[/] [dim]scroll[/]   [b]c[/] [dim]cart[/]",
            classes="footer",
        )


class CartPanel(Vertical):
    BINDINGS = [("escape", "blur")]

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="content auto-focus"):
            yield Label("name")
            yield Input("", placeholder="Your name")
            yield Label("Credit card")
            yield Input("", placeholder="XXXX-XXXX-XXXX-XXXX")
            yield Label("Address 1")
            yield Input()
            yield Label("Address 2")
            yield Input()
            yield Label("Zip / Postcode")
            yield Input()
            yield Button("Place order", variant="success")

        yield Label(
            "[b]tab[/] [dim]next[/]   [b]shift+tab[/] [dim]previous[/]  [b]escape[/] [dim]exit form[/dim]",
            classes="footer",
        )

    def action_blur(self) -> None:
        if self.app.focused:
            self.query_one(VerticalScroll).focus()

    @work
    async def on_button_pressed(self):
        self.query_one(".content").loading = True
        self.notify("Nothing is really happening. Please wait five seconds.")
        await asyncio.sleep(5)
        self.notify("And we are back. Again, nothing happened.")
        self.query_one(".content").loading = False


class Header(Container):
    active_panel = reactive("shop", recompose=True)

    def compose(self) -> ComposeResult:
        active_panel = self.active_panel
        yield Label("[b not dim]terminal")
        yield Label(
            "[not dim]s[/] shop", classes="active" if active_panel == "shop" else ""
        )
        yield Label(
            "[not dim]a[/] about", classes="active" if active_panel == "about" else ""
        )
        yield Label(
            "[not dim]f[/] faq", classes="active" if active_panel == "faq" else ""
        )
        yield Label(
            "[not dim]c[/] cart", classes="active" if active_panel == "cart" else ""
        )


class CoffeeApp(App):
    CSS_PATH = "coffee.tcss"
    DEFAULT_CLASSES = "narrow"

    active_panel: reactive[str] = reactive("shop")

    BINDINGS = [
        ("s", "switch_panel('shop')"),
        ("a", "switch_panel('about')"),
        ("f", "switch_panel('faq')"),
        ("c", "switch_panel('cart')"),
        ("q", "quit"),
    ]

    def compose(self) -> ComposeResult:
        with Column():
            with Center():
                yield Header().data_bind(CoffeeApp.active_panel)
            with ContentSwitcher(initial="shop"):
                yield ProductsPanel(id="shop")
                yield AboutPanel(id="about")
                yield FAQPanel(id="faq")
                yield CartPanel(id="cart")

    def on_app_focus(self) -> None:
        self.query("ContentSwitcher #shop .auto-focus").first().focus()

    def action_switch_panel(self, panel: str) -> None:
        self.active_panel = panel
        self.query_one(ContentSwitcher).current = panel
        self.query(f"ContentSwitcher #{panel} .auto-focus").first().focus()

    def on_resize(self, event: Resize) -> None:
        self.query_one("Screen").set_class(self.size.width < 60, "narrow")


if __name__ == "__main__":
    app = CoffeeApp()
    app.run()
