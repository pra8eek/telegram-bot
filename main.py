from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
import telegram
import logging
import praw

# INSERT RELEVANT DATA HERE
telegram_token = ""
reddit_id = ""
reddit_secret = ""

updater = Updater(token=telegram_token, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

reddit = praw.Reddit(client_id=reddit_id,
                     client_secret=reddit_secret,
                     user_agent='pra8eek')


def getContext(context, update, message):
    print("\n", context.args, sep="")
    try:
        time = context.args[-1]
        if time in ["day", "week", "month", "year", "all"]:
            try:
                k = int(context.args[-2])
                if k > 10:
                    k = 10
                    context.bot.send_message(
                        chat_id=update.effective_chat.id, text=message)
            except e:
                k = 1

        else:
            time = "day"
            try:
                k = int(context.args[-1])
                if k > 10:
                    k = 10
                    context.bot.send_message(
                        chat_id=update.effective_chat.id, text=message)
            except e:
                k = 1
    except e:
        k = 1
        time = "day"

    return k, time


def imageFetch(subreddit, time, k, update, context):
    fetched = False
    kcopy = k
    sent = 0

    while not fetched:

        fetchCount = 0
        print("Searching")
        for submission in reddit.subreddit(subreddit).top(time_filter=time,
                                                          limit=k):
            if submission.url[-3:] == "jpg":
                fetchCount += 1

        if fetchCount >= kcopy:
            sent = 0
            unsent = 0
            fetched = True
            print("Sending ")

            for submission in reddit.subreddit(subreddit).top(time_filter=time,
                                                              limit=k):
                if submission.url[-3:] == "jpg":
                    try:
                        context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=submission.url)
                        sent += 1
                        print(submission.url)

                    except e:
                        context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=submission.url)
                        sent += 1
                        print("ERROR..!!!", submission.url)

                    if sent == kcopy:
                        print("Sent")
                        break
        else:
            k = k * 2
            if k > 100:
                time = "all"
            if k > 200:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="This subreddit cannot fulfil your request")
                print("Invalid request..!!!")
                return

    if sent < kcopy:
        print("Sent | Not all")
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Unable to send " + str(kcopy - sent) +
                                 " image(s) as JPEG!!!")


def meme(update, context):
    k, time = getContext(
        context, update, "Sorry babe! But you won't be getting more than 10 posts")
    fetched = False
    kcopy = k

    try:
        subr = context.args[0]
        if subr == "menu":
            print("[MEMES] Only menu requested\n")
            fetched = True
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Here are the categories: ttt | cricket | ouija | code | meirl | gay")
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Happy to add more. You already know the developer")
            return
        elif subr == "code":
            subreddit = "ProgrammerHumor"
        elif subr == "ouija":
            subreddit = "jesuschristuoija"
        elif subr == "ttt":
            subreddit = "technicallythetruth"
        elif subr == "cricket":
            subreddit = "cricketshitpost"
        elif subr == "meirl":
            subreddit = "me_irl"
        elif subr == "gay":
            subreddit = "SuddenlyGay"
        elif subr == "custom":
            try:
                subreddit = context.args[1]
            except:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="WTF!!! Where's the subreddit bro")
                fetched = True
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Not a valid category!!! But the memes are still on")
            subreddit = "2meirl4meirl"
    except:
        subreddit = "2meirl4meirl"

    if not fetched:
        print("\n[MEMES] Requested", k, "post(s) from",
              subreddit, "subreddit with", time, "filter\n")
        imageFetch(subreddit, time, k, update, context)


def joke(update, context):
    k, time = getContext(
        context, update, "Sorry babe! But you won't be getting more than 10 jokes")
    print("[JOKE] Requested", k, "posts with", time, "filter\n")

    for submission in reddit.subreddit("jokes").top(time_filter=time, limit=k):
        joke = "*" + str(submission.title) + "*"
        joke += "\n\n" + submission.selftext
        context.bot.send_message(chat_id=update.effective_chat.id, text=joke,
                                 parse_mode=telegram.ParseMode.MARKDOWN)

    print("Sent")


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Ah shit! Here we go again")


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('meme', meme))
dispatcher.add_handler(CommandHandler('joke', joke))

updater.start_polling()
