import time
from functools import wraps
from threading import Thread
import pika
import json
import numpy as np
import pandas as pd
import plotly.express as px
import queue
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

host='rabbitmq'
queue_name = 'test'

def run_in_thread(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        ctx = get_script_run_ctx()
        add_script_run_ctx(thread, ctx)
        thread.start()
    return wrapper


@run_in_thread
def consume1():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        if message=='start':
            st.session_state.messages1=[]
        else:
            st.session_state.messages1.append(json.loads(message))

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

@run_in_thread
def consume2():  
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        if message=='start':
            st.session_state.messages2=[]
        else:
            st.session_state.messages2.append(json.loads(message))

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

@st.fragment(run_every=0.1)
def write():
    st.write(st.session_state.messages)

@st.fragment(run_every=0.5)
def plot():
    df1 = pd.DataFrame(st.session_state.messages1)
    if st.session_state.messages1 == []:
        df1 = pd.DataFrame([],columns=['x','y'])
    fig1 = px.line(df1,x='x',y='y')
    st.plotly_chart(fig1,key=1)

    df2 = pd.DataFrame(st.session_state.messages2)
    if st.session_state.messages2 == []:
        df2 = pd.DataFrame([],columns=['x','y'])
    fig2 = px.line(df2,x='x',y='y')
    st.plotly_chart(fig2,key=2)


st.session_state.messages1 = []
st.session_state.messages2 = []

def main():
    st.title("Live Data:")
    consume1()
    consume2()
    plot()
    

if __name__ == '__main__':
    main()

