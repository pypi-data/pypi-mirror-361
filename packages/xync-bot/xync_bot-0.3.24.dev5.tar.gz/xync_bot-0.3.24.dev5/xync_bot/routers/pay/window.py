from asyncio import sleep

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from xync_bot.routers.pay.dep import edt

from xync_bot import Store
from xync_bot.routers.pay import cd, dep


async def type_select(msg: Message):
    """Step 1: Select type"""
    store: Store = msg.bot.store
    ist: bool = store.curr.is_target
    rm = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Банковская валюта", callback_data=cd.MoneyType(is_fiat=1, is_target=ist).pack()
                ),
                InlineKeyboardButton(
                    text="Крипта", callback_data=cd.MoneyType(is_fiat=0, is_target=store.curr.is_target).pack()
                ),
            ]
        ]
    )
    txt = "Что нужно?" if store.curr.is_target else "Чем платишь?"
    if store.perm.msg_id:
        await edt(msg, txt, rm)
    else:
        msg = await msg.answer(txt, reply_markup=rm)
        store.perm.msg_id = msg.message_id


async def cur_select(msg: Message):
    """Common using cur func"""
    builder = InlineKeyboardBuilder()
    ist: bool = msg.bot.store.curr.is_target
    for cur_id, ticker in msg.bot.store.glob.curs.items():
        builder.button(text=ticker + dep.flags[ticker], callback_data=cd.Cur(id=cur_id, is_target=ist))
    builder.button(text="Назад к выбору типа", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(3, 3, 3, 3, 3, 1)
    sfx = "ую нужно" if ist else "ой платишь"
    await msg.edit_text("Выбери валюту котор" + sfx, reply_markup=builder.as_markup())


async def coin_select(msg: Message):
    """Common using coin func"""
    builder = InlineKeyboardBuilder()
    store: Store = msg.bot.store
    for coin_id, ticker in store.glob.coins.items():
        builder.button(text=ticker, callback_data=cd.Coin(id=coin_id, is_target=store.curr.is_target))
    builder.button(
        text="Назад к выбору типа",
        callback_data=cd.PayNav(to=cd.PayStep.t_type if store.curr.is_target else cd.PayStep.s_type),
    )
    builder.adjust(1)
    sfx = "ую нужно" if store.curr.is_target else "ой платишь"
    await msg.edit_text("Выберите монету котор" + sfx, reply_markup=builder.as_markup())


async def ex_select(msg: Message):
    store: Store = msg.bot.store
    ist = store.curr.is_target
    coin_id = getattr(store.pay, ("t" if ist else "s") + "_coin_id")
    builder = InlineKeyboardBuilder()
    for ex_id in store.glob.coinexs[coin_id]:
        builder.button(text=store.glob.exs[ex_id], callback_data=cd.Ex(id=ex_id, is_target=ist))
    builder.button(
        text="Назад к выбору монеты", callback_data=cd.PayNav(to=cd.PayStep.t_coin if ist else cd.PayStep.s_coin)
    )
    builder.button(text="Домой", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(1)
    keyboard = builder.as_markup()
    await msg.edit_text("На какую биржу?" if ist else "С какой биржи?", reply_markup=keyboard)


async def pm(msg: Message):
    store: Store = msg.bot.store
    ist = store.curr.is_target
    cur_id = getattr(store.pay, ("t" if ist else "s") + "_cur_id")
    builder = InlineKeyboardBuilder()
    for pmcur_id in store.glob.curpms[cur_id]:
        builder.button(text=store.glob.pms[pmcur_id], callback_data=cd.Pm(pmcur_id=pmcur_id, is_target=ist))
    builder.button(
        text="Назад к выбору валюты", callback_data=cd.PayNav(to=cd.PayStep.t_cur if ist else cd.PayStep.s_cur)
    )
    builder.button(text="Домой", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(1)
    keyboard = builder.as_markup()
    await msg.edit_text("На какую платежную систему?" if ist else "C какой платежной системы?", reply_markup=keyboard)


async def fill_cred_dtl(msg: Message):
    builder = InlineKeyboardBuilder()
    store: Store = msg.bot.store
    txt = "В"
    if cred_ids := store.perm.cur_creds.get(store.pay.t_pmcur_id):
        for cred_id in cred_ids:
            cred = store.perm.creds[cred_id]
            txt = f"{cred.detail}\n{cred.name}"
            if cred.extra:
                txt += f" ({cred.extra})"
            builder.button(text=txt, callback_data=cd.Cred(id=cred_id))
        txt = "Выберите реквизиты куда нужно получить деньги, если в списке нет нужных, то\nв"

    builder.button(text="Назад к выбору платежной системы", callback_data=cd.PayNav(to=cd.PayStep.t_pm))
    builder.button(text="Домой", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(2)

    await msg.edit_text(
        f"{txt}ведите номер для {store.glob.pms[store.pay.t_pmcur_id]}:", reply_markup=builder.as_markup()
    )


async def fill_cred_name(msg: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад к вводу реквизитов", callback_data=cd.PayNav(to=cd.PayStep.t_cred_dtl))
    builder.button(text="Домой", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(2)
    store: Store = msg.bot.store
    cur = store.glob.curs[store.pay.t_cur_id]
    payment = store.glob.pms[store.pay.t_pmcur_id]
    detail = store.pay.cred_dtl
    await edt(msg, f"{cur}:{payment}:{detail}: Введите имя получателя", builder.as_markup())


async def amount(msg: Message):
    """Step 5: Filling target amount"""
    builder = InlineKeyboardBuilder()
    store: Store = msg.bot.store
    if store.curr.is_fiat:
        cur_coin = store.glob.curs[store.pay.t_cur_id]
        builder.button(text="Назад к вводу имени", callback_data=cd.PayNav(to=cd.PayStep.t_cred_name))
        t_name = store.glob.pms[store.pay.t_pmcur_id]
    else:
        cur_coin = store.glob.curs[store.pay.t_coin_id]
        builder.button(text="Назад к выбору биржи", callback_data=cd.PayNav(to=cd.PayStep.t_ex))
        t_name = store.glob.exs[store.pay.t_ex_id]

    builder.button(text="Домой", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(2)

    await msg.edit_text(f"Введите нужную сумму {cur_coin} для {t_name}", reply_markup=builder.as_markup())


async def set_ppo(msg: Message):
    rm = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Нет", callback_data="ppo:1"),
                InlineKeyboardButton(text="Да", callback_data="ppo:2"),
            ],
            [InlineKeyboardButton(text="Да хоть на 3", callback_data="ppo:3")],
        ]
    )
    await msg.edit_text("На 2 платежа сможем разбить?", reply_markup=rm)


async def set_urgency(msg: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="1 мин", callback_data=cd.Time(minutes=1))
    builder.button(text="5 мин", callback_data=cd.Time(minutes=5))
    builder.button(text="30 мин", callback_data=cd.Time(minutes=30))
    builder.button(text="3 часа", callback_data=cd.Time(minutes=180))
    builder.button(text="сутки", callback_data=cd.Time(minutes=60 * 24))
    builder.button(text="Назад к вводу платежей", callback_data=cd.PayNav(to=cd.PayStep.t_pm))
    builder.button(text="Домой", callback_data=cd.PayNav(to=cd.PayStep.t_type))
    builder.adjust(2, 2, 1, 1, 1)
    await msg.edit_text("Сколько можешь ждать?", reply_markup=builder.as_markup())


async def run_timer(message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="Платеж получен", callback_data=cd.Action(act=cd.ActionType.received))

    data = await state.get_value("timer")
    seconds = data * 60

    def format(sec):
        days = sec // (24 * 3600)
        sec %= 24 * 3600
        hours = sec // 3600
        sec %= 3600
        minutes = sec // 60
        sec %= 60

        if days > 0:
            return f"{days}д {hours:02d}:{minutes:02d}:{sec:02d}"
        elif hours > 0:
            return f"{hours:02d}:{minutes:02d}:{sec:02d}"
        else:
            return f"{minutes:02d}:{sec:02d}"

    try:
        await message.edit_text(f"⏳ Осталось {format(seconds)}", reply_markup=builder.as_markup())
    except Exception:
        return

    while seconds > 0:
        await sleep(1)
        seconds -= 1
        try:
            await message.edit_text(f"⏳ Осталось {format(seconds)}", reply_markup=builder.as_markup())
            await state.update_data(timer=seconds)
        except Exception:
            break

    if seconds <= 0:
        builder = InlineKeyboardBuilder()
        builder.button(text="Платеж получен", callback_data=cd.Action(act=cd.ActionType.received))
        builder.button(text="Денег нет", callback_data=cd.Action(act=cd.ActionType.not_received))
        try:
            await message.edit_text("⏳ Время вышло!", reply_markup=builder.as_markup())
        except Exception:
            pass
