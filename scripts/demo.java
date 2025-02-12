//命名空间
import com.beisen.workflow.trigger.common.TriggerDataSource;
import java.util.HashMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
//ImportEnd
//参数名称、参数说明、参数类型
//processVariableDic,流程变量,HashMap<String,String>
public TriggerDataSource Main(HashMap<String, String> processVariableDic)
        {
        String url="https://prod.hzbeacon.com:8002/api/hr/entry/notify";
        httpInvoke("POST",url,gson.toJson(processVariableDic));
        return null;
        }
public String httpInvoke(String method,String url,String body){
        InputStream in=null;
        PrintWriter out=null;
        try{
        HttpURLConnection connection=(HttpURLConnection)new URL(url).openConnection();
        connection.setRequestMethod(method);
        connection.setDoInput(true);
        connection.setDoOutput(true);
        connection.setUseCaches(false);
        connection.addRequestProperty("Content-Type","application/json");
        connection.addRequestProperty("X-PAAS-Tenant-ID",String.valueOf(context.getTenantID()));
        connection.addRequestProperty("X-PAAS-User-ID",String.valueOf(context.getUserID()));

        connection.connect();
        if(!"GET".equals(method)){
        out=new PrintWriter(connection.getOutputStream());
        out.print(body);
        out.flush();
        }
        in=connection.getInputStream();
        BufferedReader buffer=new BufferedReader(new InputStreamReader(in,"UTF-8"));
        StringBuffer sb=new StringBuffer();
        String line=null;
        while((line=buffer.readLine())!=null){
        sb.append(line);
        }
        String result=sb.toString();
        return result;
        }catch(IOException e){
        e.printStackTrace();
        //logger.error("doRequest", e);
        throw new RuntimeException(e.getMessage(),e);
        }finally{
        try{
        if(in!=null){
        in.close();
        }
        if(out!=null){
        out.close();
        }
        }catch(IOException e){
        e.printStackTrace();
        }
        }
        }

